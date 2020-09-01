import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import h5py
import requests, os
from gwpy.timeseries import TimeSeries
from gwosc.locate import get_urls
from gwosc import datasets
from gwosc.api import fetch_event_json
import corner

# -- Default detector list
detectorlist = ['H1','L1', 'V1']

# Title the app
st.title('Gravitational Wave Parameter Viewer')

st.markdown("""
 * Use the controls at left to select data
 * Learn more at https://gw-openscience.org
""")

#-- Make data directory, if needed
if not os.path.exists('./data'):
    os.mkdir('./data')

@st.cache   #-- Magic command to cache data
def load_gw(t0, detector):
    strain = TimeSeries.fetch_open_data(detector, t0-16, t0+16, cache=False)
    return strain

@st.cache
def load_pe(url):

    # -- Try to read PE samples from disk
    # -- If not available, download
    
    # -- Get file name
    fn = 'data/' + os.path.split(url)[1]
    tries = 0 
    while tries < 3:
        try:
            data = h5py.File(fn)
            key0 = list(data.keys())[0]
            try:
                dataarray = data['Overall_posterior'][()]
                waveform = 'Overall_posterior'
                break
            except:
                dataarray = data[key0][()]
                waveform = key0
                break
        except:
            tries += 1
            data.close()
            # -- Download PE file
            r = requests.get(url, allow_redirects=True)
            with open(fn, 'wb') as newfile:
                newfile.write(r.content)
            
    data.close()
    return dataarray, waveform


st.sidebar.markdown("## Select Data Time and Detector")

# -- Get list of events
# find_datasets(catalog='GWTC-1-confident',type='events')
eventlist = datasets.find_datasets(type='events', catalog='GWTC-1-confident')
eventlist = [name.split('-')[0] for name in eventlist if name[0:2] == 'GW']
eventset = set([name for name in eventlist])
eventlist = list(eventset)
eventlist.sort()


chosen_event = st.sidebar.selectbox('Select Event', eventlist)
t0 = datasets.event_gps(chosen_event)
detectorlist = list(datasets.event_detectors(chosen_event))
detectorlist.sort()
    
    
#-- Choose detector as H1, L1, or V1
detector = st.sidebar.selectbox('Detector', detectorlist)

# Create a text element and let the reader know the data is loading.
strain_load_state = st.text('Loading data...this may take a minute')
try:
    strain = load_gw(t0, detector)
except:
    st.text('Data load failed.  Try a different time and detector pair.')
    raise st.ScriptRunner.StopException
    
strain_load_state.text('Loading data...done!')

# -- Tell the user which event we are looking at
st.markdown('## {}'.format(chosen_event))

#-- Crop the data
cropstart = t0-0.2
cropend   = t0+0.1
center = int(t0)
strain = strain.crop(center-16, center+16)


# -- Plot the whitened, band-passed data
# -- Whiten and bandpass data
st.subheader('Whitened and Bandbassed Data')
white_data = strain.whiten()
bp_data = white_data.bandpass(30, 400)
fig3 = bp_data.crop(cropstart, cropend).plot()
st.pyplot(fig3, clear_figure=True)

# -- Make a Q-transform
st.subheader('Q-transform')

st.sidebar.markdown('## Q-Transform Controls')
dtboth = st.sidebar.slider('Time Range (seconds)', 0.1, 8.0, 1.0)  # min, max, default
dt = dtboth / 2.0
vmax = st.sidebar.slider('Colorbar Max Energy', 10, 500, 25)  # min, max, default

qcenter = st.sidebar.slider('Q-value', 5, 120, 5)  # min, max, default
qrange = (int(qcenter*0.8), int(qcenter*1.2))


hq = strain.q_transform(outseg=(t0-dt, t0+dt), qrange=qrange)
fig4 = hq.plot()
ax = fig4.gca()
fig4.colorbar(label="Normalised energy", vmax=vmax, vmin=0)
ax.grid(False)
ax.set_yscale('log')
ax.set_ylim(bottom=15)
st.pyplot(fig4, clear_figure=True)


#-- Try getting pe url
jsoninfo = fetch_event_json(chosen_event, catalog='GWTC-1-confident')
#st.write(jsoninfo)

for name, nameinfo in jsoninfo['events'].items():
    for peset, peinfo in nameinfo['parameters'].items():
        if 'pe' in peset:
            sourceurl = peinfo['data_url']
            
        
st.write('PE samples URL: ', sourceurl)
            
pedata, waveform = load_pe(sourceurl)

st.write('Showing samples for {}'.format(waveform))



#st.write('Got some samples')
#st.write(pedata.dtype.names)
paramlist = pedata.dtype.names

# -- Try a corner plot
m_names = ['m1_detector_frame_Msun', 'm2_detector_frame_Msun']

m1 = pedata['m1_detector_frame_Msun']
m2 = pedata['m2_detector_frame_Msun']

corner_data = np.array(list(zip(m1, m2))) 
corner.corner(corner_data, labels=[r'$m_1 ~($M$_\odot)$', r'$m_2 ~($M$_\odot)$'], color='dodgerblue')
st.pyplot()

for param in paramlist:

    plt.figure()
    plt.hist(pedata[param], bins=50, density=True)
    plt.xlabel(param)
    st.pyplot()
    plt.close('all')
    
    



st.subheader("About this app")
st.markdown("""
This app displays data from LIGO, Virgo, and GEO downloaded from
the Gravitational Wave Open Science Center at https://gw-openscience.org .
""")
