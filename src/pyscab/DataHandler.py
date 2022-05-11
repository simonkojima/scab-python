import numpy
import time
import os
import wave

class DataHandler(object):
    def __init__(self, frame_rate = 44100, verbose=True):
        self.pcm_data = list()
        self.n_ch = list()
        self.n_frames = list()
        self.path = list()
        self.id = list()
        self.volume = list()
        self.frame_rate = frame_rate
        self.sample_width = list()
        self.verbose = verbose
        self.dtype = numpy.dtype("int16")

    def load(self, id, path, volume=1.0):
        if self._is_exist_id(id) is False:
            self.id.append(id)
        else:
            raise ValueError("Passed id " + str(id) + " is dumplicated.")

        f_name = os.path.basename(path)

        wf = wave.open(path, 'rb')
        n_ch = wf.getnchannels()

        sw = wf.getsampwidth()
        if sw == 1:
            self.dtype = dtype = numpy.dtype("uint8")
        elif sw == 2:
            self.dtype = dtype = numpy.dtype("int16")
        else:
            raise ValueError("file must be Int16 or UInt8 PCM wave format")

        nf = wf.getnframes()

        if self.verbose:
            start = time.time()
            print("start loading : " + f_name)

        data = numpy.zeros((nf, n_ch)).astype(dtype)

        data_wav = wf.readframes(nf)
        data_wav = numpy.frombuffer(data_wav, dtype=dtype)
        data_wav = data_wav * volume
        data_wav = data_wav.astype(dtype)
        for ch in range(n_ch):
            data[:, ch] = data_wav[ch::n_ch]

        if self.verbose:
            print("finish loading : " + str(f_name))
            end = time.time()
            print("elapsed time : " + str(end-start))

        self.path.append(path)
        self.pcm_data.append(data)
        self.n_ch.append(n_ch)
        self.sample_width.append(sw)
        self.n_frames.append(nf)
        self.volume.append(volume)

    def apply_window(self, id, t_raise_fall):

        n_frames = self.get_nframes_by_id(id)
        fs = self.frame_rate

        raise_ = numpy.arange(0, int(t_raise_fall*fs))
        fall_ = numpy.arange(int(t_raise_fall*fs), 0, -1)

        raise_ = raise_ / max(raise_)
        fall_ = fall_ / max(fall_)

        flat = numpy.ones((n_frames - numpy.size(raise_) - numpy.size(raise_)))

        win_filter = numpy.concatenate([raise_, flat, fall_])

        idx = self._id2idx(id)
        n_ch = self.n_ch[idx]

        win = numpy.zeros((numpy.size(win_filter), n_ch))
        for m in range(n_ch):
            win[:, m] = win_filter

        self.pcm_data[idx] = self.pcm_data[idx]*win
        self.pcm_data[idx] = self.pcm_data[idx].astype(self.dtype)
    
    def add_pcm(self, id, data):
        if self._is_exist_id(id) is False:
            self.id.append(id)
        else:
            raise ValueError("Passed id " + str(id) + " is dumplicated.")

        self.path.append("PCM")
        self.pcm_data.append(data)
        self.n_frames.append(data.shape[0])
        self.n_ch.append(data.shape[1])

    def get_nframes_by_id(self, id):
        return numpy.shape(self.get_data_by_id(id))[0]

    def get_length_by_id(self, id):
        return self.get_nframes_by_id(id)/self.frame_rate

    def get_data_by_id(self, id):
        idx = self._id2idx(id)
        return self.pcm_data[idx]

    def get_n_ch_by_id(self):
        idx = self._id2idx(id)
        return self.n_ch[idx]

    def _id2idx(self, id):
        idx = numpy.where(numpy.array(self.id) == id)
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