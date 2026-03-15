import streamlit as st
from skyfield.api import Loader
from datetime import datetime
import folium
from streamlit_folium import st_folium

# Caches Skyfield loaders and TLE parsing for best efficiency
@st.cache_resource(ttl=3600)
def load_iss_satellite():
    load = Loader('./skyfield_data')
    tle_url = 'https://celestrak.org/NORAD/elements/stations.txt'
    satellites = load.tle_file(tle_url)
    iss = next((sat for sat in satellites if sat.name == 'ISS (ZARYA)'), None)
    if iss is None:
        raise RuntimeError("ISS (ZARYA) not found in TLE data.")
    ts = load.timescale()
    return iss, ts

def get_iss_position(iss, ts):
    t = ts.now()
    subpoint = iss.at(t).subpoint()
    lat = subpoint.latitude.degrees
    lon = subpoint.longitude.degrees
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return lat, lon, timestamp

def main():
    st.set_page_config(page_title="Live ISS Tracker", layout="wide")
    st.title("🛰️ Live International Space Station (ISS) Tracker")

    try:
        iss, ts = load_iss_satellite()
    except Exception as e:
        st.error(f"Error loading ISS satellite data: {e}")
        return

    # Either update on load or when button clicked
    if 'iss_data' not in st.session_state:
        lat, lon, timestamp = get_iss_position(iss, ts)
        st.session_state.iss_data = {'lat': lat, 'lon': lon, 'timestamp': timestamp}
    else:
        lat = st.session_state.iss_data['lat']
        lon = st.session_state.iss_data['lon']
        timestamp = st.session_state.iss_data['timestamp']

    if st.button("Refresh ISS Position"):
        lat, lon, timestamp = get_iss_position(iss, ts)
        st.session_state.iss_data = {'lat': lat, 'lon': lon, 'timestamp': timestamp}
        st.success("ISS position updated!")

    # Display the map
    m = folium.Map(location=[lat, lon], zoom_start=2, tiles="cartodb positron")
    folium.Marker([lat, lon], tooltip="ISS", icon=folium.Icon(color="red", icon="rocket")).add_to(m)
    st_folium(m, width=1000, height=600)

    st.markdown(f"**Current Latitude:** `{lat:.4f}°` &nbsp;&nbsp;&nbsp; **Longitude:** `{lon:.4f}°`")
    st.markdown(f"*Last updated:* `{timestamp}`")

    st.info("Click the button to fetch the latest ISS position.")

if __name__ == "__main__":
    main()
