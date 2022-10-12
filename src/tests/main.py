import pyscab

file_dirs = list()
file_dirs.append("./tests/440Hz_stereo.wav")


#------------------------------------------------
# load audio files
#

afh = pyscab.DataHandler()
afh.load(1, file_dirs[0], volume = 0.7)

#------------------------------------------------
# generate sine wave
#

sine = pyscab.generate_pcm(number_of_channels=2, frequency=440, duration=1, format="INT16", volume=0.7, window=None)
afh.add_pcm(2, sine)

#------------------------------------------------
# audio play plan
#

# plan format
# [time, file_id, ch, marker]

audio_plan = list()

audio_plan.append([0.5, 1, [1,2], 1])
audio_plan.append([1.5, 2, [1,2], 2])


#------------------------------------------------
# open and initialize Audio I/F
#

DEVICE_NAME = 'X-AIR ASIO Driver'
#DEVICE_NAME = 'ASIO4ALL v2'
#DEVICE_NAME = 'default'
ahc = pyscab.AudioInterface(device_name = DEVICE_NAME, n_ch = 2, format="INT16", frames_per_buffer = 512)

def marker_send(val):
    print("marker sent : " + str(val))

from multiprocessing import Array
share = Array('d', range(8))
share = [0 for m in range(8)]

stc = pyscab.StimulationController(ahc, marker_send=marker_send, share=share, correct_latency = True, correct_hardware_buffer = True)
stc.play(audio_plan, afh)