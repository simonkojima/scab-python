import numpy as np
import time
import os
import wave
from logging import getLogger
logger = getLogger('pyscab.'+__name__)

class DataHandler(object):
    """
    Handling wav files and pcm data.

    Parameters
    ----------
    frame_rate : int, default=44100
        frame rate of data.
    verbose : bool, default=False
        verbosity while data loading.

    Attributes
    ----------
    pcm_data : list
        loaded audio data.
    n_ch : list of int
        number of channels of loaded audio data.
    n_frames : list of int
        number of frames of loaded audio data.
    paths : list of str
        path of loaded audio file.
    id : list of int
        id of loaded audio data.
    volume : list of float
        volume of loaded audio data.
    frame_rate : int
        frame rate of data
    sample width : list of int
        sample width in byte of loaded audio data.
    dtype : np.dtype
        data format type.
    """   

    def __init__(self, frame_rate = 44100, verbose=False):
        self.pcm_data = list()
        self.n_ch = list()
        self.n_frames = list()
        self.paths = list()
        self.id = list()
        self.volume = list()
        self.frame_rate = frame_rate
        self.sample_width = list()
        self.verbose = verbose
        self.dtype = np.dtype("int16")

    def load(self, id, path, volume=1.0):
        """
        Load wav file by path.

        Parameters
        ----------
        id : int
            id for this audio data.
        path : str
            file path of audio file to be loaded.
        volume : float, default=1.0
            volume for this audio data.

        Raises
        ------
        ValueError
            Raises ValueError if existing (already been used) id is passed to id.
        ValueError
            Raises ValueError if format of loaded wav file is not Int16 or UInt8.

        Examples
        --------
        You just need to specify the id for data, and file path to be loaded.

        >>> import pyscab
        >>> dh = pyscab.DataHandler()
        >>> dh.load(1, path = "/home/USER/Music/something.wav", volume = 0.5)
        """
        if self._is_exist_id(id) is False:
            self.id.append(id)
        else:
            raise ValueError("Passed id " + str(id) + " is dumplicated.")

        f_name = os.path.basename(path)

        wf = wave.open(path, 'rb')
        n_ch = wf.getnchannels()

        # it should be set in __init__()
        sw = wf.getsampwidth()
        if sw == 1:
            self.dtype = dtype = np.dtype("uint8")
        elif sw == 2:
            self.dtype = dtype = np.dtype("int16")
        else:
            raise ValueError("file must be Int16 or UInt8 PCM wave format")

        nf = wf.getnframes()

        if self.verbose:
            start = time.time()
            print("start loading : " + f_name)

        logger.debug("start loading : %s", path)
        data = np.zeros((nf, n_ch)).astype(dtype)

        data_wav = wf.readframes(nf)
        data_wav = np.frombuffer(data_wav, dtype=dtype)
        data_wav = data_wav * volume
        data_wav = data_wav.astype(dtype)
        for ch in range(n_ch):
            data[:, ch] = data_wav[ch::n_ch]

        if self.verbose:
            print("finish loading : " + str(f_name))
            end = time.time()
            print("elapsed time : " + str(end-start))

        self.paths.append(path)
        self.pcm_data.append(data)
        self.n_ch.append(n_ch)
        self.sample_width.append(sw)
        self.n_frames.append(nf)
        self.volume.append(volume)

    def apply_window(self, id, t_raise_fall):
        """
        Applying window function to data specified by id.

        Parameters
        ----------
        id : int
            data id to be applied filter function.
        t_raise_fall : float
            time duration for raise and fall.

        Notes
        -----
        If r_raise_fall is set to 0.05. Both raising and falling time will be set to 0.05.
        Currently, only linear function can be applied. Other function will be implemented in the future.
        """

        n_frames = self.get_nframes_by_id(id)
        fs = self.frame_rate

        raise_ = np.arange(0, int(t_raise_fall*fs))
        fall_ = np.arange(int(t_raise_fall*fs), 0, -1)

        raise_ = raise_ / max(raise_)
        fall_ = fall_ / max(fall_)

        flat = np.ones((n_frames - np.size(raise_) - np.size(raise_)))

        win_filter = np.concatenate([raise_, flat, fall_])

        idx = self._id2idx(id)
        n_ch = self.n_ch[idx]

        win = np.zeros((np.size(win_filter), n_ch))
        for m in range(n_ch):
            win[:, m] = win_filter

        self.pcm_data[idx] = self.pcm_data[idx]*win
        self.pcm_data[idx] = self.pcm_data[idx].astype(self.dtype)
    
    def add_pcm(self, id, data):
        """
        Add the pcm audio data (matrix) to DataHandler.

        Parameters
        ----------
        id : int
            id for this audio data.
        data : np.ndarray
            audio data. shoule have shape of (number of samples, number of channels)

        Notes
        -----
        File path will be automatically set to "PCM"

        Raises
        ------
        ValueError
            Raises ValueError if existing (already been used) id is passed to id.
        """
        if self._is_exist_id(id) is False:
            self.id.append(id)
        else:
            raise ValueError("Passed id " + str(id) + " is dumplicated.")

        if data.ndim == 1:
            data = np.atleast_2d(data)
            data = data.transpose()

        self.paths.append("PCM")
        self.pcm_data.append(data)
        self.n_frames.append(data.shape[0])
        self.n_ch.append(data.shape[1])

    def get_nframes_by_id(self, id):
        """
        get number of frames of the audio data specified by id.

        Parameters
        ----------
        id : int
            id of audio data.

        Returns
        -------
        number_of_frames : int
            number of frames of the audio data specified by id.
        """
        return np.shape(self.get_data_by_id(id))[0]

    def get_length_by_id(self, id):
        """
        get length (in seconds) of the audio data specified by id.

        Parameters
        ----------
        id : int
            id of audio data.

        Returns
        -------
        length : int
            length (in seconds) of the audio data specified by id.
        """
        # return type in second.
        return self.get_nframes_by_id(id)/self.frame_rate

    def get_data_by_id(self, id):
        """
        get data of the audio data specified by id.

        Parameters
        ----------
        id : int
            id of audio data.

        Returns
        -------
        data : np.ndarray
            audio data array specified by id.
        """
        idx = self._id2idx(id)
        return self.pcm_data[idx]

    def get_n_ch_by_id(self, id):
        """
        get number of channels of the audio data specified by id.

        Parameters
        ----------
        id : int
            id of audio data.

        Returns
        -------
        number_of_channels : int
            number of channels of audio data specified by id.
        """
        idx = self._id2idx(id)
        return self.n_ch[idx]

    def get_path_by_id(self,id):
        """
        get file path of the audio data specified by id.

        Parameters
        ----------
        id : int
            id of audio data.

        Returns
        -------
        path : str
            file path of audio data specified by id.
        """
        idx = self._id2idx(id)
        return self.paths[idx]

    def _id2idx(self, id):
        idx = np.where(np.array(self.id) == id)
        if len(idx[0]) == 0:
            return None
            #raise ValueError("id does not exist.")
        else:
            return int(idx[0])

    def _is_exist_id(self, id):
        if self._id2idx(id) == None:
            return False
        else:
            return True