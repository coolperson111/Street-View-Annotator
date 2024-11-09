import base64
import os
from pathlib import Path

from fasthtml import *
from fasthtml import FastHTML, serve
from fasthtml.common import *

from src.utils.processor import process_location

app = FastHTML()

lat = 30.72
long = 76.72

panorama, depth_map, heading_degrees, latitude, longitude, pano_id = process_location(
    lat, long
)
image_url = ""
if panorama is not None:
    image_path = Path("panorama_image.jpg")
    panorama.save(image_path)
    image_url = (
        f"data:image/jpeg;base64,{base64.b64encode(image_path.read_bytes()).decode()}"
    )


@app.get("/")
def home():
    with open("./src/ui/map_final.html", "r") as f:
        content1 = f.read()

    with open("./viewer_template.html", "r") as f:
        content2 = f.read()
        content2 = content2.replace("{{image_url}}", image_url)

    return Titled(
        "Horizontal Layout",
        Div(
            Div(NotStr(content1), cls="half"),
            Div(NotStr(content2), cls="half"),
            style="display: flex; gap: 10px;",
        ),
    )


serve()
