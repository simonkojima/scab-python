import numpy
import time
import os
import wave

class DataHandler(object):
    def __init__(self, verbose=True):
        self.pcm_data = list()
        self.n_ch = list()
        self.n_frames = list()
        self.path = list()
        self.id = list()
        self.volume = list()
        self.verbose = verbose

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
            dtype = numpy.dtype("uint8")
        elif sw == 2:
            dtype = numpy.dtype("int16")
        else:
            raise ValueError("file must be Int16 or UInt8 PCM wave format")

        nf = wf.getnframes()

        if self.verbose:
            start = time.time()
            print("start loading : " + f_name)

        data = numpy.zeros((nf, n_ch))

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
        #self.sample_width.append(sw)
        self.n_frames.append(nf)
        self.volume.append(volume)
    
    def add_pcm(self, id, data):
        if self._is_exist_id(id) is False:
            self.id.append(id)
        else:
            raise ValueError("Passed id " + str(id) + " is dumplicated.")

        self.path.append("PCM")
        self.pcm_data.append(data)
        self.n_frames.append(data.shape[0])
        self.n_ch.append(data.shape[1])
        

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
        else:
            return int(idx[0])

    def _is_exist_id(self, id):
        if self._id2idx(id) == None:
            return False
        else:
            return True