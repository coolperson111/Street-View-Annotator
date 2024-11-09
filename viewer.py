import base64
import os
from pathlib import Path

import streamlit as st
from flask import Flask, jsonify, request
from flask_cors import CORS

from src.utils.database import Database
from src.utils.processor import process_location

st.set_page_config(page_title="Panorama Viewer", layout="wide")
st.html("<style> .main {overflow: hidden} </style>")


app = Flask(__name__)
CORS(app)


@app.route("/markers", methods=["POST"])
def receive_marker():
    data = request.get_json()
    yaw = data.get("yaw")
    pitch = data.get("pitch")
    print(f"Received marker: yaw={yaw}, pitch={pitch}")

    return jsonify({"status": "success", "message": "Marker received"}), 200


def generate_pannellum_viewer(image_url):
    with open("viewer_template.html", "r") as f:
        html_template = f.read()
    html = html_template.replace("{image_url}", image_url)
    return html


lat = 30.72
long = 76.72

col1, col2 = st.columns([1, 1], gap="small")

with col1:
    panorama, depth_map, heading_degrees, latitude, longitude, pano_id = (
        process_location(lat, long)
    )

    if panorama is not None:
        image_path = Path("panorama_image.jpg")
        panorama.save(image_path)
        image_url = f"data:image/jpeg;base64,{base64.b64encode(image_path.read_bytes()).decode()}"
        viewer_html = generate_pannellum_viewer(image_url)
        st.components.v1.html(viewer_html, height=600, scrolling=False)
        os.remove(image_path)
    else:
        st.error("No panorama found for the given location.")

with col2:
    html_file_path = "./src/ui/map_final.html"
    with open(html_file_path, "r") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=600, scrolling=False)


if __name__ == "__main__":
    app.run(port=5001)
