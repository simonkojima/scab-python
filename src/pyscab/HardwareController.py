import pyaudio
import numpy as np
from logging import getLogger
logger = getLogger('pyscab.'+__name__)

class CallbackParams(object):
    """
    class for referencing parameters of callback function of portaudio.

    Attributes
    ----------
    data : list of pyscab.ReadAudioChunk
        containing audio data to play.
    data_finished : list of bool
        True if all audio data in attribute data which has corresponding index were played.
    """
    def __init__(self):
        self.init()
    
    def init(self):
        """
        initialize all parameters hold by CallbackParams instance.
        """
        self.data = list()
        self.data_finished = list()
        self.format = None
        self.time = None
        self.n_ch = None
        self.data_callback = None

callback_params = CallbackParams()

def callback(in_data, frame_count, time_info, status, p=callback_params):
    #data = np.zeros((frame_count, p.n_ch), dtype=p.format)
    p.data_callback.fill(0)
    for idx, is_finished in enumerate(p.data_finished):
    #for idx_audio, audio in enumerate(p.data):
    #for audio in p.data:
        if is_finished is False:
            chunk = p.data[idx].read_chunk()
            for idx_ch, ch in enumerate(p.data[idx].get_ch()):
                p.data_callback[:, ch-1] += chunk[:, idx_ch]
        #else:
        #    p.data_finished[idx] = True
            # if all audio chunks were loaded, delete the instance
            #
            # deleted this in ver. 0.0.6, since doing this will take time and makes problem with presenting short audio with fast SOA.
            #del p.data[idx_audio]
    p.time = time_info
    return (np.ravel(p.data_callback, order='C'), pyaudio.paContinue)

def get_available_devices():
    """
    print available devices connected to the computer.
    """
    pya = pyaudio.PyAudio()
    hi = HardwareInformation(pya)
    devices = hi.devices
    for device in devices:
        print("name : '" + str(devices[device]['name']) + "', maxOutputChannels : " + str(devices[device]['maxOutputChannels']))


class HardwareInformation(object):
    """
    get hardware information of audio devices.

    Attributes
    ----------
    devices : dict
        containes device name and maximum number of output channels of each device. 
        keys : 'name', 'maxOutputChannels'
    """
    def __init__(self, pya):
        self.devices = dict()
        n_devs = pya.get_device_count()
        for idx in range(n_devs):
            device = pya.get_device_info_by_index(idx)
            name = device['name']
            if device['maxOutputChannels'] > 0 and name not in self.devices:
                self.devices[name] = device

    def get_output_device_with_name(self, device_name):
        """
        get device information by name.

        Parameters
        ----------
        device_name : str
            name of the device.

        Returns
        -------
        device : pyaudio.PaDeviceInfo
        """
        return self.devices[device_name]

class AudioInterface(object):
    """
    Class for handling Audio Interface device.

    Attributes
    ----------
    device_name : str
        name of the device to be opened.
    format : str {'INT16', 'UINT8'}
        format to be used for device.
    frame_rate : int
        frame rate of device.
    frames_per_butter : int
        frames per buffer
    pya : instance of pyaudio.PyAudio()
        instance of PyAudio device.
    device_idx : int
        device index of opened device.
    num_cannels : int
        number of channels to be opened.
    n_ReadAudioChunk_obj : int
        total number of ReadAudioChunk instance.

    See Also
    --------
    Class ReadAudioChunk : used for reading audio data by chunk.
    """
    def __init__(self,
                 device_name=None,
                 n_ch = 2,
                 format="INT16",
                 frame_rate=44100,
                 frames_per_buffer=512,):
        """
        set audio device to be used and its settings

        Parameters
        ----------
        device_name : str, default=None
            device name to be opened.
            If it's None, 'default' will be used for Linux and 'ASIO4ALL' for Windows.
        n_ch : int, default=2
            number of channels to be opened
        format : {'INT16', 'UINT8'}, default='INT16'
            audio data fortmat to be played
        frame_rate : int, default=44100
            frame rate of audio device.
        frames_per_butter : int, default=512
            frames per butter of audio device. Which means chunk size of audio data read in callback function will be set to this value.
        """
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
            self.format_np = np.dtype("int16")
        elif format.upper() == "UINT8":
            self.format_pyaudio = pyaudio.paUInt8
            self.format_np = np.dtype("uint8")
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
        """
        open audio device.
        """
        callback_params.init()
        self.n_ReadAudioChunk_obj = 0
        callback_params.n_ch = self.num_channels
        callback_params.format = self.format_np
        callback_params.data_callback = np.zeros((self.frames_per_buffer, self.num_channels), dtype=self.format_np)
        self.stream = self.pya.open(format=self.format_pyaudio,
                                    channels=self.num_channels,
                                    frames_per_buffer=self.frames_per_buffer,
                                    output_device_index=self.device_idx,
                                    rate=self.frame_rate,
                                    output=True,
                                    stream_callback=callback)

    def play(self, data, ch):
        """
        play audio data from specified channel.

        Parameters
        ----------
        data : np.ndarray
            audio data which have a shape of (number of samples, number of channels)
        ch : list of int
            channel number of audio device to be played (start from 1)

        Examples
        --------
        In this case, audio_data will be played from 1st channel of audio device.

        >>> play(audio_data, [1])
        """
        callback_params.data.append(ReadAudioChunk(data, self.frames_per_buffer, ch, format = self.format_np, idx_obj = self.n_ReadAudioChunk_obj))
        callback_params.data_finished.append(False)
        self.n_ReadAudioChunk_obj += 1 # should be add 1 after executing appending ReadAudioChunk obj.

    def get_time_info(self):
        """
        get time information from portaudio (PaStreamCallbackTimeInfo)

        Returns
        -------
        time_info : dict
        """
        return callback_params.time

    def close(self):
        """
        stop audio stream and close device.
        """
        self.stream.stop_stream()
        self.stream.close()

    def terminate(self):
        """
        terminate portaudio.
        """
        self.pya.terminate()

class ReadAudioChunk(object):
    """
    reading audio data by chunk.

    Attributes
    ----------
    data : np.ndarray
        audio data.
    n_ch_data : int
        number of channels of audio data
    n_frames : int
        number of frames of audio data
    chunk_sixe : int
        chunk size.
    ch : list of int
        channel number of device which audio data will be played.
    format : np.dtype
        audio data format
    finished : Bool
        If True, all audio data have already been read. If False, there's remained data.
    idx_obj : int
        id of instance.
    """
    def __init__(self, data, chunk_size, ch, volume=1.0, format = np.dtype("int16"), idx_obj = None):
        """
        load data with specified settings

        Parameteres
        ----------
        data : np.ndarray
            audio data.
        chunk_sixe : int
            chunk size.
        ch : list of int
            channel number of device which audio data will be played.
        format : np.dtype, default=np.dtype('int16')
            audio data format
        idx_obj : int, default=None
            id of instance.
        """
        self.data = data.astype(format)
        self.n_ch_data = data.shape[1] # n_ch of data
        self.n_frames = data.shape[0]
        self.current_idx = 0
        self.chunk_size = chunk_size
        self.ch = ch # ch num to be stimuli presented
        self.format = format
        #self.remained_frames = self.n_frames
        self.finished = False
        self.idx_obj = idx_obj # will be change to id
        self.chunk_data = np.zeros((self.chunk_size, self.n_ch_data), dtype=self.format)
        # if mono audio will be played from multiple channel,
        # concatenate it to multiple channel matrix
        # in order to make computational load in portaudio callback function less
        while self.n_ch_data < len(self.ch):
            self.data = np.hstack((self.data,self.data))
            self.n_ch_data = self.data.shape[1]

    def read_chunk(self):
        """
        read audio data by chunk.

        Returns
        -------
        chunk_data : np.ndarray
            chunk data which have a shape of (chunk size, number of channels)
        """

        start = self.current_idx*self.chunk_size
        end = (self.current_idx*self.chunk_size)+self.chunk_size

        if end >= (self.n_frames-1):
            self.chunk_data.fill(0)
            self.chunk_data[0:(self.n_frames-start-1),:] = self.data[start:-1,:]
            
            #=====================
            #This is old method.
            #
            #deleted in ver 0.0.6 since it is slow.
            #=====================
            # padding zero to last block 
            #data = self.data[start:-1,:]
            #n_padding = self.chunk_size - data.shape[0]
            #data = np.vstack((data, np.zeros((n_padding, self.n_ch_data), dtype=self.format)))
            #data = np.vstack((data, np.zeros((n_padding, self.n_ch_data))))
            #self.finished = True
            #=====================
            callback_params.data_finished[self.idx_obj] = True
        else:
            self.chunk_data = self.data[start:end,:]
            #self.remained_frames -= self.chunk_size
        self.current_idx += 1
        return self.chunk_data

    def is_finished(self):
        """
        check if it's finished

        Returns
        -------
        is_finished : bool
            True if all data already been read, False if there's remained data.
        """
        return self.finished

    def get_ch(self):
        """
        get channel number to play the audio data.

        Returns
        -------
        channel : list of int
            channel number which audio data will be played.
        """
        return self.ch
