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
    st.text('Downloading: ' , url)
    fn = os.path.basename(url)
    with open(fn,'wb') as strainfile:                 
        straindata = requests.get(url)
        strainfile.write(straindata.content)

    # -- Read strain data
    strain = TimeSeries.read(fn,format='hdf5.losc')

    # -- Clean-up temporary file
    os.remove(fn)
    
    #strain = TimeSeires.fetch_open_data(detector, t0-16, t0+16)
    return strain


# -- Set a GPS time:
t0 = 1126259462.4    # -- GW150914

#-- Choose detector as H1, L1, or V1
detector = 'H1'


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
dt = 1  #-- Set width of q-transform plot, in seconds
hq = strain.q_transform(outseg=(t0-dt, t0+dt))
fig4 = hq.plot()
ax = fig4.gca()
fig4.colorbar(label="Normalised energy")
ax.grid(False)
ax.set_yscale('log')
st.pyplot(fig4)




DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache   #-- Magic command to cache data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data(10000)
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done! Now with cacheing!')

#st.subheader('Raw data')
#st.write(data)

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

#-- Just creates a heading
st.subheader('Number of pickups by hour')  

# -- Histogram by hour
hist_values = np.histogram(
    data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]

# print(hist_values)
st.write(hist_values)

st.bar_chart(hist_values)


st.subheader('Try matplotlib')

arr = np.random.normal(1, 1, size=100)
plt.hist(arr, bins=20)
st.pyplot()


st.subheader('Map of all pickups')
st.map(data)


st.subheader('Filtered map')

hour_to_filter = st.slider('hour', 0, 23, 17)  # min: 0h, max: 23h, default: 17h

filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
st.subheader(f'Map of all pickups at {hour_to_filter}:00')
st.map(filtered_data)
