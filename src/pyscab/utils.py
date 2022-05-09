
def generate_pcm(number_of_channels=1, frequency=440, duration = 1.0, volume = 1.0, fs=44100, format="INT16", window = "linear", t_raise_fall = 0.01):
    import numpy
    t = numpy.arange(0, duration, 1/fs)
    sin = volume * numpy.sin(2*numpy.pi*frequency*t)

    if window is None:
        pass
    elif window.upper() == "LINEAR":
        #import sys
        #import matplotlib.pyplot as plt
        raise_ = numpy.arange(0, int(t_raise_fall*fs))
        fall_ = numpy.arange(int(t_raise_fall*fs), 0, -1)

        raise_ = raise_ / max(raise_)
        fall_ = fall_ / max(fall_)
        flat = numpy.ones((int((duration-2*t_raise_fall)*fs)))

        win_filter = numpy.concatenate([raise_, flat, fall_])

        sin = sin * win_filter

    if format.upper() == "INT16":
        dt = numpy.dtype("int16")
        sin = sin * 32767
        sin = sin.astype(dt)
        # FOR DEBUGGING
        if max(sin) > 32767 or min(sin) < -32768:
            raise ValueError("ERROR : generate_pcm() in utils.py, error happened in type conversion. int16")
    elif format.upper() == "UINT8":
        dt = numpy.dtype("uint8")
        sin = ((sin*0.5)+0.5)*255
        sin = sin.astype(dt)
        # FOR DEBUGGING
        if max(sin) > 255 or min(sin) < 0:
            raise ValueError("ERROR : generate_pcm() in utils.py, error happened in type conversion. uint8")
    else:
        raise ValueError("Unknown Format : " + format + ". It can only take INT16 or UINT8.")
    
    if number_of_channels > 1:
        n_frames = len(sin)
        #print(n_frames)
        sin = numpy.reshape(sin, (n_frames, 1))
        sin = numpy.repeat(sin, number_of_channels, axis=1)

    return sin

    

