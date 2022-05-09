import time

def get_required_time(plans, data, frame_rate):
    end_times = list()
    for plan in plans:
        end_time = data.get_nframes_by_id(plan[1])/frame_rate
        end_time += plan[0]
        end_times.append(end_time)
    return max(end_times)

class StimulationController(object):

    def __init__(self, AudioHardwareController, marker_send, time_tick = 0.0001):
        self.ahc = AudioHardwareController
        self.time_tick = time_tick
        self.running = False
        self.marker_send = marker_send

    def play(self, plans, data, time_termination = 'auto'):

        # initialize
        del_idxs = list()
        if time_termination is None:
            # TODO : prep two functions for main_loop with and w/o termination with time
            #        to avoid verbosed conditional branch in loop
            time_termination = float('inf')
        elif time_termination.lower() == 'auto':
            time_termination = get_required_time(plans, data, self.ahc.frame_rate)

        self.running = True
        self.ahc.open()

        # requires time to be opened. with out this line, time_info won't be get
        # TO DO : get the state of instance from pyaudio and wait until it's opened instead of waiting with sleep
        time.sleep(1)        

        start = self.ahc.get_time_info()['current_time']
        while self.running is True:
            now = self.ahc.get_time_info()['current_time'] - start
            for idx, plan in enumerate(plans):
                if now > plan[0]:
                    self.ahc.play(data.get_data_by_id(plan[1]),plan[2])
                    self.marker_send(val=plan[3])
                    del_idxs.append(int(idx))
                for del_idx in del_idxs:
                    del plans[del_idx]
                del_idxs=list()
            time.sleep(self.time_tick)
            if now > time_termination:
                self.running = False

        #time.sleep(1)
        self.ahc.close()