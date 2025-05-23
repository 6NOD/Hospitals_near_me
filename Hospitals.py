
import streamlit as st
import streamlit.components.v1 as components
import requests

GOOGLE_API_KEY = "YOUR_GOOGLE_PLACES_API_KEY"

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

def fetch_hospitals(lat, lon):
    url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lon}&radius=5000&type=hospital&key={GOOGLE_API_KEY}"
    )
    response = requests.get(url)
    return response.json()

def main():
    st.set_page_config(page_title="Nearby Hospitals", layout="centered")
    st.title("Find Nearest Hospitals")
    get_browser_location()

    msg = st.experimental_get_query_params().get("msg", [None])[0]
    if msg:
        try:
            lat, lon = map(str.strip, msg.split(","))
            st.success(f"Your Location: {lat}, {lon}")
            results = fetch_hospitals(lat, lon)

            if "results" in results:
                st.write("**Nearby Hospitals:**")
                for hospital in results["results"]:
                    name = hospital.get("name", "Unknown")
                    address = hospital.get("vicinity", "")
                    gmap_link = f"https://www.google.com/maps/search/?api=1&query={hospital['geometry']['location']['lat']},{hospital['geometry']['location']['lng']}"
                    st.markdown(f"**{name}**  \n{address}  \n[View on Map]({gmap_link})")
            else:
                st.warning("No hospitals found.")
        except Exception as e:
            st.error("Error parsing location or fetching hospitals.")
    else:
        st.info("Please allow location access in your browser.")

if __name__ == "__main__":
    main()
