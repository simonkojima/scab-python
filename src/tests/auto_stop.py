#import pyscab

import sys
import os
import pathlib
import time

path_tests = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(path_tests)[0:-5])

import HardwareController
import StimulationController
import DataHandler
import utils

file_dirs = list()
file_dirs.append("./440Hz_stereo.wav")

#------------------------------------------------
# load audio files
#

afh = DataHandler.DataHandler()
afh.load(1, file_dirs[0], volume = 0.7)
afh.load(2, file_dirs[0], volume = 1)

#------------------------------------------------
# generate sine wave
#

sine = utils.generate_pcm(number_of_channels=2, frequency=440, duration=5, format="INT16", volume=0.7, window='linear')
afh.add_pcm(3, sine)

#------------------------------------------------
# audio play plan
#

# plan format
# [time, file_id, ch, marker]

audio_plan = list()

audio_plan.append([0, 1, [1,2], 1])
audio_plan.append([1, 2, [1,2], 2])
audio_plan.append([2, 3, [1,2], 2])
#------------------------------------------------
# open and initialize Audio I/F
#

#DEVICE_NAME = 'X-AIR ASIO Driver'
#DEVICE_NAME = 'ASIO4ALL v2'
DEVICE_NAME = 'default'
ahc = HardwareController.AudioInterface(device_name = DEVICE_NAME, n_ch = 2, format="INT16", frames_per_buffer = 512)

def marker_send(val):
    print("marker sent : " + str(val))

stc = StimulationController.StimulationController(ahc, marker_send=marker_send)

stc.play(audio_plan, afh, time_termination='auto')
ahc.terminate()