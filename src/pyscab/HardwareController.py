import pyaudio
import numpy
from logging import getLogger
logger = getLogger('pyscab.'+__name__)

class CallbackParams(object):
    def __init__(self):
        self.init()
    
    def init(self):
        self.data = list()
        self.data_finished = list()
        self.format = None
        self.time = None
        self.n_ch = None

callback_params = CallbackParams()

def callback(in_data, frame_count, time_info, status, p=callback_params):
    data = numpy.zeros((frame_count, p.n_ch), dtype=p.format)
    for idx, is_finished in enumerate(p.data_finished):
    #for idx_audio, audio in enumerate(p.data):
    #for audio in p.data:
        if is_finished is False:
            chunk = p.data[idx].read_chunk()
            for idx_ch, ch in enumerate(p.data[idx].get_ch()):
                data[:, ch-1] += chunk[:, idx_ch]
        #else:
        #    p.data_finished[idx] = True
            # if all audio chunks were loaded, delete the instance
            #
            # deleted this in ver. 0.0.6, since doing this will take time and makes problem with presenting short audio with fast SOA.
            #del p.data[idx_audio]
    p.time = time_info
    return (numpy.ravel(data, order='C'), pyaudio.paContinue)

def get_available_devices():
    pya = pyaudio.PyAudio()
    hi = HardwareInformation(pya)
    devices = hi.devices
    for device in devices:
        print("name : '" + str(devices[device]['name']) + "', maxOutputChannels : " + str(devices[device]['maxOutputChannels']))


class HardwareInformation(object):
    def __init__(self, pya):
        self.devices = dict()
        n_devs = pya.get_device_count()
        for idx in range(n_devs):
            device = pya.get_device_info_by_index(idx)
            name = device['name']
            if device['maxOutputChannels'] > 0 and name not in self.devices:
                self.devices[name] = device

    def get_output_device_with_name(self, device_name):
        return self.devices[device_name]

class AudioInterface(object):
    def __init__(self,
                 device_name=None,
                 n_ch = 2,
                 format="INT16",
                 frame_rate=44100,
                 frames_per_buffer=512,):
        if device_name is None:
            import platform
            if platform.system() == "Linux":
                self.device_name = "default"
            elif platform.system() == "Windows":
                self.device_name = "ASIO4ALL v2"
            else:
                raise ValueError("Unknown Operating System")
        else:
            self.device_name = device_name 

        self.format = format
        if format.upper() == "INT16":
            self.format_pyaudio = pyaudio.paInt16
            self.format_numpy = numpy.dtype("int16")
        elif format.upper() == "UINT8":
            self.format_pyaudio = pyaudio.paUInt8
            self.format_numpy = numpy.dtype("uint8")
        else:
            raise ValueError("Unknown Format : " + self.format + ". It can only take INT16 or UINT8.")
        self.frame_rate = frame_rate
        self.frames_per_buffer = frames_per_buffer

        self.pya = pya = pyaudio.PyAudio()
        hardware_information = HardwareInformation(pya)

        available_devices = hardware_information.devices
        logger.debug("Audio Device '%s' was selected.", self.device_name)
        device = available_devices[self.device_name]
        self.device_idx = device['index']
        self.num_channels = n_ch

        self.n_ReadAudioChunk_obj = 0


    def open(self):
        callback_params.init()
        self.n_ReadAudioChunk_obj = 0
        callback_params.n_ch = self.num_channels
        callback_params.format = self.format_numpy
        self.stream = self.pya.open(format=self.format_pyaudio,
                                    channels=self.num_channels,
                                    frames_per_buffer=self.frames_per_buffer,
                                    output_device_index=self.device_idx,
                                    rate=self.frame_rate,
                                    output=True,
                                    stream_callback=callback)

    def play(self, data, ch):
        callback_params.data.append(ReadAudioChunk(data, self.frames_per_buffer, ch, format = self.format_numpy, idx_obj = self.n_ReadAudioChunk_obj))
        callback_params.data_finished.append(False)
        self.n_ReadAudioChunk_obj += 1 # should be add 1 after executing appending ReadAudioChunk obj.

    def get_time_info(self):
        return callback_params.time

    def close(self):
        self.stream.stop_stream()
        self.stream.close()

    def terminate(self):
        self.pya.terminate()

class ReadAudioChunk(object):
    def __init__(self, data, chunk_size, ch, volume=1.0, format = numpy.dtype("int16"), idx_obj = None):
        self.data = data.astype(format)
        self.n_ch_data = data.shape[1] # n_ch of data
        self.n_frames = data.shape[0]
        self.current_idx = 0
        self.chunk_size = chunk_size
        self.ch = ch # ch num to be stimuli presented
        self.format = format
        #self.remained_frames = self.n_frames
        self.finished = False
        self.idx_obj = idx_obj

        # if mono audio will be played from multiple channel,
        # concatenate it to multiple channel matrix
        # in order to make computational load in portaudio callback function less
        while self.n_ch_data < len(self.ch):
            self.data = numpy.hstack((self.data,self.data))
            self.n_ch_data = self.data.shape[1]

    def read_chunk(self):
        start = self.current_idx*self.chunk_size
        end = (self.current_idx*self.chunk_size)+self.chunk_size

        if end >= (self.n_frames-1):
            data = numpy.zeros((self.chunk_size, self.n_ch_data), dtype=self.format)
            data[0:(self.n_frames-start-1),:] = self.data[start:-1,:]
            """
            =====================
            This is old method.
            
            deleted in ver 0.0.6 since it is slow.
            =====================
            # padding zero to last block 
            data = self.data[start:-1,:]
            n_padding = self.chunk_size - data.shape[0]
            data = numpy.vstack((data, numpy.zeros((n_padding, self.n_ch_data), dtype=self.format)))
            #data = numpy.vstack((data, numpy.zeros((n_padding, self.n_ch_data))))
            """
            #self.finished = True
            callback_params.data_finished[self.idx_obj] = True
        else:
            data = self.data[start:end,:]
            #self.remained_frames -= self.chunk_size
        self.current_idx += 1
        return data

    def is_finished(self):
        return self.finished

    def get_ch(self):
        return self.ch
