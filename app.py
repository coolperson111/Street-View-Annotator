import folium
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static

st.set_page_config(layout="wide", page_title="Map with Sidebar")


@st.cache_data
def load_data():
    countries = pd.read_csv("./assets/locations/countries.csv")
    states = pd.read_csv("./assets/locations/states.csv")
    cities = pd.read_csv("./assets/locations/cities.csv")
    return countries, states, cities


countries_df, states_df, cities_df = load_data()

map_types = {
    "OpenStreetMap": {
        "url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        "attribution": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        "name": "OpenStreetMap",
    },
    "Esri Satellite": {
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attribution": "Esri",
        "name": "Esri Satellite",
    },
    "Esri Labels": {
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        "attribution": "Esri",
        "name": "Esri Labels",
    },
}

coordinates = [
    (20.5937, 78.9629),
    (19.0760, 72.8777),
    (28.6139, 77.2090),
    (22.5726, 88.3639),
    (13.0827, 80.2707),
    (12.9716, 77.5946),
    (17.3850, 78.4867),
    (25.2950, 82.9876),
    (23.8103, 90.4125),
    (21.1702, 72.8311),
]

st.sidebar.title("Map Options")

selected_map_type = st.sidebar.selectbox("Select Map Type", list(map_types.keys()))

selected_country = st.sidebar.selectbox(
    "Select Country", [""] + list(countries_df["name"].unique())
)

selected_state = ""
selected_city = ""

if selected_country:
    selected_state = st.sidebar.selectbox(
        "Select State",
        [""]
        + list(
            states_df[states_df["country_name"] == selected_country]["name"].unique()
        ),
    )

if selected_state:
    selected_city = st.sidebar.selectbox(
        "Select City",
        [""]
        + list(cities_df[cities_df["state_name"] == selected_state]["name"].unique()),
    )

st.title("Interactive Map")

center_lat, center_lon, zoom = None, None, 5
location = ""

if selected_city:
    city_data = cities_df[cities_df["name"] == selected_city].iloc[0]
    center_lat, center_lon = city_data["latitude"], city_data["longitude"]
    zoom = 11
    location = selected_city
elif selected_state:
    state_data = states_df[states_df["name"] == selected_state].iloc[0]
    center_lat, center_lon = state_data["latitude"], state_data["longitude"]
    zoom = 8
    location = selected_state
elif selected_country:
    country_data = countries_df[countries_df["name"] == selected_country].iloc[0]
    center_lat, center_lon = country_data["latitude"], country_data["longitude"]
    zoom = 5
    location = selected_country

if center_lat is None or center_lon is None:
    center_lat, center_lon = 20.5937, 78.9629

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=zoom,
    tiles=None,
)

for layer_name, layer_data in map_types.items():
    folium.TileLayer(
        tiles=layer_data["url"],
        attr=layer_data["attribution"],
        name=layer_data["name"],
        overlay=False,
        control=True,
    ).add_to(m)

folium.TileLayer(
    tiles=map_types[selected_map_type]["url"],
    attr=map_types[selected_map_type]["attribution"],
).add_to(m)

filtered_coordinates = coordinates

st.sidebar.markdown(
    f"""
    <div style="background-color:#f0f0f5; padding: 20px; border-radius: 10px;">
        <h2 style="color: #4CAF50;">🌍 Location</h2>
        <p style="font-size:20px; color: #000000"><strong>{location}</strong></p>
        <h2 style="color: #4CAF50;">🌳 Total Trees</h2>
        <p style="font-size:20px; color: #000000;"><strong>{len(filtered_coordinates)}</strong></p>
    </div>
    """,
    unsafe_allow_html=True,
)

for lat, lon in coordinates:
    popup_content = f"""
    <div style="width: 200px">
        <h4>Location Information</h4>
        <p><strong>Latitude:</strong> {lat:.8f}</p>
        <p><strong>Longitude:</strong> {lon:.8f}</p>
        <p>Add any additional information here.</p>
    </div>
    """

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_content, max_width=300),
        icon=folium.Icon(icon="leaf", color="green"),
    ).add_to(m)


folium.plugins.Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
).add_to(m)

folium_static(m, width=1000, height=480)
