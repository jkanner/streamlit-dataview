import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


import requests, os
from gwpy.timeseries import TimeSeries
from gwosc.locate import get_urls

# Title the app
st.title('GWpy Plotting App')


@st.cache   #-- Magic command to cache data
def load_gw(t0, detector):
    url = get_urls(detector, t0, t0)[-1]
    print(url)
    fn = os.path.basename(url)
    with open(fn,'wb') as strainfile:                 
        straindata = requests.get(url)
        strainfile.write(straindata.content)

    # -- Read strain data
    strain = TimeSeries.read(fn,format='hdf5.losc')

    # -- Clean-up temporary file
    os.remove(fn)
    
    #strain = TimeSeries.fetch_open_data(detector, t0-16, t0+16)
    return strain


# -- Set a GPS time:
st.sidebar.markdown("### Select detector and GPS time")

#-- Choose detector as H1, L1, or V1
detector = st.sidebar.selectbox('Detector', ['H1', 'L1', 'V1'])

str_t0 = st.sidebar.text_input('GPS Time', '1126259462.4')    # -- GW150914
t0 = float(str_t0)

st.sidebar.markdown("""
You might try some of these examples times in the H1 detector:
 * 1126259462.4    (GW150914) 
 * 1187008882.4    (GW170817) 
 * 933200215       (hardware injection)
 * 1132401286.33   (Koi Fish Glitch) 
""")





# Create a text element and let the reader know the data is loading.
strain_load_state = st.text('Loading data...')
strain = load_gw(t0, detector)
strain_load_state.text('Loading data...done!')

#-- Make a time series plot    
center = int(t0)
strain = strain.crop(center-16, center+16)
fig1 = strain.plot()
st.pyplot(fig1)



# -- Try whitened and band-passed plot
# -- Whiten and bandpass data
st.subheader('Whitened Data')
white_data = strain.whiten()
bp_data = white_data.bandpass(30, 400)
fig3 = bp_data.plot()
plt.xlim(t0-0.2, t0+0.1)
st.pyplot(fig3)

st.subheader('Q-transform')

st.sidebar.markdown('## Q-Transform Controls')
dt = st.sidebar.slider('Time Range', 0.1, 4.0, 1.0)  # min, max, default

# dt = 1  #-- Set width of q-transform plot, in seconds
hq = strain.q_transform(outseg=(t0-dt, t0+dt))
fig4 = hq.plot()
ax = fig4.gca()
fig4.colorbar(label="Normalised energy")
ax.grid(False)
ax.set_yscale('log')
st.pyplot(fig4)


