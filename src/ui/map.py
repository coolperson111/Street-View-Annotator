from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QColorDialog, QHBoxLayout, QInputDialog, QLabel,
                             QLineEdit, QListWidget, QListWidgetItem,
                             QPushButton, QSlider, QVBoxLayout, QWidget)

from utils.processor import *
from utils.utils import save_image


class FoliumWidget(QWidget):
    def __init__(self, main_window, gl_widget):
        super().__init__()
        self.gl_widget = gl_widget
        self.main_window = main_window
        self.markers = []
        self.Polygons = []
        self.init_ui()
        self.folder_path = "Output"

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # for entering coordinates
        # self.coord_input = QLineEdit(self)
        # layout.addWidget(self.coord_input)

        # to trigger the coordinate update
        update_button = QPushButton("Save Map", self)
        update_button.clicked.connect(self.update_map_with_input)
        layout.addWidget(update_button)

        # to get the panorama
        panorama_button = QPushButton("Get Panorama", self)
        panorama_button.clicked.connect(self.main_window.get_panorama)
        layout.addWidget(panorama_button)

        # to trigger polygon drawing
        add_button = QPushButton("Add Markers", self)
        add_button.clicked.connect(self.add_marker)
        layout.addWidget(add_button)

        # to remove the marker
        remove_button = QPushButton("Remove Markers", self)
        remove_button.clicked.connect(self.remove_marker)
        layout.addWidget(remove_button)

        # to display the Folium map
        web_view = QWebEngineView()
        web_view.setHtml(open("src/ui/map_final.html").read())
        layout.addWidget(web_view)

        # # to annotate
        # add_button = QPushButton("Annotate", self)
        # add_button.clicked.connect(self.add_vertice)
        # layout.addWidget(add_button)
        #
        # # to trigger marker removal
        # remove_polygons_button = QPushButton("Remove Polygons", self)
        # remove_polygons_button.clicked.connect(self.remove_Polygons)
        # layout.addWidget(remove_polygons_button)

    def update_map_with_input(self):
        save_image(
            self.findChild(QWebEngineView),
            self.main_window.latitude,
            self.main_window.longitude,
        )
        save_image(
            self.gl_widget.image,
            self.gl_widget.lat,
            self.gl_widget.lng,
            self.gl_widget.fov,
            self.gl_widget.pitch,
            self.gl_widget.yaw,
            street=True,
        )

    def add_marker(self):
        for lat, lng in self.gl_widget.coordinates_stack:
            update_script = f"newTree({lat}, {lng});"
            self.findChild(QWebEngineView).page().runJavaScript(update_script)
            self.markers.append((lat, lng))

    def remove_marker(self):
        remove_script = f"removeMarker();"
        self.findChild(QWebEngineView).page().runJavaScript(remove_script)
        self.markers = []

    # def save_map_as_png(self):
    #     folder_path = "Output"
    #     if not folder_path.lower().endswith(".png"):
    #         folder_path += ".png"
    #     self.findChild(QWebEngineView).grab().save(folder_path)
    #     print(f"Map saved as PNG: {folder_path}")

    # def add_vertice(self):
    #     add_script = "annotate();"
    #     self.findChild(QWebEngineView).page().runJavaScript(add_script)

    # def remove_Polygons(self):
    #     remove_script = "removePolygons();"
    #     self.findChild(QWebEngineView).page().runJavaScript(remove_script)
    #     self.Polygons = []

    # def get_annotation(self):
    #     if len(self.gl_widget.coordinates_stack) >= 3:
    #         polygon_vertices = ",".join(
    #             [f"[{lat},{lng}]" for lat, lng in self.gl_widget.coordinates_stack]
    #         )
    #         draw_polygon_script = f"drawPolygon([{polygon_vertices}], '{self.gl_widget.map_color_name}', {self.gl_widget.map_transparency});"
    #         self.findChild(QWebEngineView).page().runJavaScript(draw_polygon_script)
    #         self.gl_widget.coordinates_stack = []
    #     else:
    #         print("At least 3 markers are required to draw a polygon.")
