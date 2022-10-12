import time
from logging import getLogger
logger = getLogger('pyscab.'+__name__)

def get_required_time(plans, data):
    end_times = list()
    for plan in plans:
        end_time = data.get_length_by_id(plan[1])
        end_time += plan[0]
        end_times.append(end_time)
    return max(end_times)

class StimulationController(object):

    def __init__(self, AudioHardwareController, marker_send, time_tick = 0.0001, share=None):
        """
        class for playing stimulating plan.

        Attributes
        ----------
        AudioHardwareController : An instance of pyscab.AudioHardwareController class
        marker_send : reference to a function
            A reference to function for send a marker
        mode : str {'serial', 'pararell'} default = 'serial'
            If it's set to 'pararell', it can be controll from parent process.
        time_tick : float, default=0.0001
            pause between each loop in play() function. In terms of real time, it should be reduced.
            However, it also caused intence compulational load.
        share : list or instance of multiprocessing class
            0 : before playing
            1 : playing
            2 : finish playing

            share[0] is used for sharing runnin status.
            When it's working in pararell mode, it will be stop playing immediate after share is changed to other than 1.
            e.g., when you are presenting stimulus in online BCI application with dynamic stopping,
            you need to stop playing when it's triggered. In that case, you need to set mode to pararell and use share variable.

            share[1] is used for sharing current marker value.

        """
        self.ahc = AudioHardwareController
        self.time_tick = time_tick
        self.marker_send = marker_send
        if share is None:
            self.share = [0 for m in range(8)]
        else:
            self.share = share
        logger.debug("time_tick for Stimulation Controller was set to %s", str(self.time_tick))

    def play(self, plans, data, time_termination = 'auto', pause=0.5):

        # initialize
        self.share[0] = 0

        del_idxs = list()
        if time_termination is None:
            # TODO : prep two functions for main_loop with and w/o termination with time
            #        to avoid verbosed conditional branch in loop
            time_termination = float('inf')
        elif time_termination.lower() == 'auto':
            time_termination = get_required_time(plans, data)
        
        logger.debug("session time was set to %s." ,str(time_termination))

        self.share[0] = 1
        self.ahc.open()
        logger.debug("Audio Hardware Controller Opening.")

        # requires time to be opened. with out this line, time_info won't be get
        # TO DO : get the state of instance from pyaudio and wait until it's opened instead of waiting with sleep
        #time.sleep(1)
        while self.ahc.get_time_info() is None:
            time.sleep(0.01)

        start = self.ahc.get_time_info()['current_time']
        while self.share[0] == 1:
            now = self.ahc.get_time_info()['current_time'] - start
            for idx, plan in enumerate(plans):
                if now > plan[0]:
                    self.ahc.play(data.get_data_by_id(plan[1]),plan[2])
                    self.marker_send(val=plan[3])
                    self.share[1] = plan[3]
                    del_idxs.append(int(idx))
                    logger.debug("Playing, id:%s, ch:%s, marker:%s, path:%s",str(plan[1]),str(plan[2]),str(plan[3]),data.get_path_by_id(plan[1]))
                for del_idx in del_idxs:
                    del plans[del_idx]
                del_idxs=list()
            time.sleep(self.time_tick)
            if now > time_termination:
                self.share[0] = 2

        time.sleep(pause)
        self.ahc.close()
        logger.debug("Audio Hardware Controller Closing.")