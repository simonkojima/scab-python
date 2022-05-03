import pyaudio
import numpy

class Share(object):
    data = list()
    format = None
    time = None
    n_ch = None

callback_params = Share()

def callback(in_data, frame_count, time_info, status, p=callback_params):
    data = numpy.zeros((frame_count, p.n_ch), dtype=p.format)
    for idx_audio, audio in enumerate(p.data):
        if audio.is_finished() is not True:
            chunk = audio.read_chunk()
        else:
            # if all audio chunks were loaded, delete the instance
            del p.data[idx_audio]
            break

        for idx_ch, ch in enumerate(audio.get_ch()):
            data[:, ch-1] += chunk[:, idx_ch]
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
                 #volume=DEFAULT_VOLUME,
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
        #self.volume = volume
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
        #self.use_headphones = use_headphones

        self.pya = pya = pyaudio.PyAudio()
        hardware_information = HardwareInformation(pya)

        available_devices = hardware_information.devices
        print(self.device_name)
        device = available_devices[self.device_name]
        self.device_idx = device['index']
        self.num_channels = n_ch


    def open(self):
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
        callback_params.data.append(ReadAudioChunk(data, self.frames_per_buffer, ch, format = self.format_numpy))

    def get_time_info(self):
        return callback_params.time

    def close(self):
        self.stream.stop_stream()
        self.stream.close()

    def terminate(self):
        self.pya.terminate()

class ReadAudioChunk(object):
    def __init__(self, data, chunk_size, ch, volume=1.0, format = numpy.dtype("int16")):
        self.data = data.astype(format)
        #self.data = data
        self.n_ch_data = data.shape[1] # n_ch of data
        self.n_frames = data.shape[0]
        self.current_idx = 0
        self.chunk_size = chunk_size
        self.ch = ch # ch num to be stimuli presented
        self.format = format
        self.finished = False

        # if mono audio will be played from multiple channel,
        # concatenate it to multiple channel matrix
        # in order to make computational load in portaudio callback function less
        while self.n_ch_data < len(self.ch):
            self.data = numpy.hstack((self.data,self.data))
            self.n_ch_data = self.data.shape[1]

    def read_chunk(self):
        start = self.current_idx*self.chunk_size
        end = (self.current_idx*self.chunk_size)+self.chunk_size
        if end > self.n_frames:
            # padding zero to last block 
            data = self.data[start:-1,:]
            n_padding = self.chunk_size - data.shape[0]
            data = numpy.vstack((data, numpy.zeros((n_padding, self.n_ch_data), dtype=self.format)))
            #data = numpy.vstack((data, numpy.zeros((n_padding, self.n_ch_data))))
            self.finished = True
        else:
            data = self.data[start:end,:]
        self.current_idx += 1
        return data

    def is_finished(self):
        return self.finished

    def get_ch(self):
        return self.ch
