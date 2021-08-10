
from scipy import signal
from scipy.io import wavfile
import io
import numpy as np

# -- Helper function to make audio file

def make_audio_file(bp_data, t0=None):
    # -- window data for gentle on/off
    window = signal.windows.tukey(len(bp_data), alpha=1.0/10)
    win_data = bp_data*window

    # -- Normalize for 16 bit audio
    win_data = np.int16(win_data/np.max(np.abs(win_data)) * 32767 * 0.9)

    fs=1/win_data.dt.value
    virtualfile = io.BytesIO()    
    wavfile.write(virtualfile, int(fs), win_data)
    
    return virtualfile
