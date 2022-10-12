
def generate_pcm(number_of_channels=1, frequency=440, duration = 1.0, volume = 1.0, fs=44100, format="INT16", window = "linear", t_raise_fall = 0.01):
    import numpy as np
    t = np.arange(0, duration, 1/fs)
    sin = volume * np.sin(2*np.pi*frequency*t)

    if window is None:
        pass
    elif window.upper() == "LINEAR":
        #import sys
        #import matplotlib.pyplot as plt
        raise_ = np.arange(0, int(t_raise_fall*fs))
        fall_ = np.arange(int(t_raise_fall*fs), 0, -1)

        raise_ = raise_ / max(raise_)
        fall_ = fall_ / max(fall_)
        flat = np.ones((int((duration-2*t_raise_fall)*fs)))

        win_filter = np.concatenate([raise_, flat, fall_])

        sin = sin * win_filter

    if format.upper() == "INT16":
        dt = np.dtype("int16")
        sin = sin * 32767
        sin = sin.astype(dt)
        # FOR DEBUGGING
        if max(sin) > 32767 or min(sin) < -32768:
            raise ValueError("ERROR : generate_pcm() in utils.py, error happened in type conversion. int16")
    elif format.upper() == "UINT8":
        dt = np.dtype("uint8")
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
        sin = np.reshape(sin, (n_frames, 1))
        sin = np.repeat(sin, number_of_channels, axis=1)

    return sin

    

