# scab-python
python implementation of scab (stimulation controller for auditory bci)  
This package allows users to present auditory stimuli for brain-computer interface. It can send marker signal to amplifier with low latency and small jitter.  
  
# Install  
You can install package from pypi by using pip.  
```
pip install pyscab
```
- requirment  
numpy and pyaudio is required to use this package.  
This package was developed and tested under python=3.8, numpy=1.22.3 and pyaudio=0.2.11. However, it may work on other version as well. (not tested)  

- Installing PyAudio (on Windows)  
DO NOT INSTALL PyAudio Package by using pip command on Windows environment, otherwise ASIO driver can't be used.  
Instead of using pip, download wheel file which is fit for your environment from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install by following command.  
```
pip install PATH_TO_WHL_FILE.whl
```
  
# Documentation  
You can find the document [here](http://pyscab.readthedocs.io/)
  
# Misc
Author : Simon Kojima  
Guest Researcher at Donders Institue, Radboud University, Nijmegen, Netherlands  
Ph.D. Stundent at Shibaura Institue of Technology, Tokyo, Japan  
