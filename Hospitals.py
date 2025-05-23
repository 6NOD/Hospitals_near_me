
import streamlit as st
import streamlit.components.v1 as components
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Nearby Hospitals (Free)", layout="centered")
st.title("Nearby Hospitals (No API Key)")

def get_browser_location():
    js = """
    <script>
    navigator.geolocation.getCurrentPosition((pos) => {
        const loc = pos.coords.latitude + "," + pos.coords.longitude;
        const iframe = document.createElement('iframe');
        iframe.setAttribute('srcdoc', `<script>window.parent.postMessage("${loc}", "*")</script>`);
        document.body.appendChild(iframe);
    });
    </script>
    """
    components.html(js, height=0)

def query_hospitals(lat, lon):
    query = f"""
[out:json];
(
  node["amenity"="hospital"](around:5000,{lat},{lon});
  way["amenity"="hospital"](around:5000,{lat},{lon});
  relation["amenity"="hospital"](around:5000,{lat},{lon});
);
out center;
"""
    response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
    return response.json()

def render_map(lat, lon, hospitals):
    m = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Marker([lat, lon], tooltip="You are here", icon=folium.Icon(color="blue")).add_to(m)
    for el in hospitals.get("elements", []):
        name = el.get("tags", {}).get("name", "Unnamed Hospital")
        if el.get("lat") and el.get("lon"):
            folium.Marker([el["lat"], el["lon"]], tooltip=name, icon=folium.Icon(color="red")).add_to(m)
        elif "center" in el:
            folium.Marker([el["center"]["lat"], el["center"]["lon"]], tooltip=name, icon=folium.Icon(color="red")).add_to(m)
    return m

get_browser_location()
msg = st.query_params().get("msg", [None])[0]
if msg:
    try:
        lat, lon = map(float, msg.split(","))
        st.success(f"Your Location: {lat}, {lon}")
        st.write("Searching for nearby hospitals...")
        hospitals = query_hospitals(lat, lon)
        if hospitals.get("elements"):
            st.write(f"**Found {len(hospitals['elements'])} hospitals nearby.**")
            m = render_map(lat, lon, hospitals)
            st_folium(m, width=700, height=500)
        else:
            st.warning("No hospitals found nearby.")
    except Exception as e:
        st.error("Failed to parse location or fetch hospital data.")
else:
    st.info("Please allow location access in your browser.")
