from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QSizePolicy, QSlider, QVBoxLayout,
                             QWidget)

from utils.database import Database
from utils.processor import *
from utils.utils import save_image


class FoliumWidget(QWidget):
    def __init__(self, main_window, gl_widget):
        super().__init__()
        self.gl_widget = gl_widget
        self.main_window = main_window
        self.markers = []
        # self.Polygons = []
        self.lat_offset = 0
        self.lng_offset = 0
        self.init_ui()
        self.folder_path = "Output"

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # for entering coordinates
        # self.coord_input = QLineEdit(self)
        # layout.addWidget(self.coord_input)

        button_layout = QGridLayout()

        # to trigger the coordinate update
        update_button = QPushButton("Save Map", self)
        update_button.clicked.connect(self.save_map_with_input)
        button_layout.addWidget(update_button, 0, 0)

        # to get the panorama
        panorama_button = QPushButton("Get Panorama", self)
        panorama_button.clicked.connect(self.main_window.get_panorama)
        button_layout.addWidget(panorama_button, 0, 1)

        # to trigger polygon drawing
        add_button = QPushButton("Add Annotations", self)
        add_button.clicked.connect(self.add_marker)
        button_layout.addWidget(add_button, 1, 0)

        # to remove the marker
        save_button = QPushButton("Save Annotations", self)
        save_button.clicked.connect(self.save_annotations)
        button_layout.addWidget(save_button, 1, 1)

        layout.addLayout(button_layout)

        # Layout for latitude offset slider and its components
        lat_slider_layout = QHBoxLayout()
        lat_slider_label = QLabel("Lat Offset:")
        lat_slider_label.setFixedWidth(80)
        self.lat_offset_slider = QSlider(Qt.Horizontal)
        self.lat_offset_slider.setMinimum(-100)
        self.lat_offset_slider.setMaximum(100)
        self.lat_offset_slider.setValue(0)
        self.lat_offset_slider.valueChanged.connect(self.on_lat_slider_change)

        self.lat_offset_input = QLineEdit("0")
        self.lat_offset_input.setFixedWidth(40)
        self.lat_offset_input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lat_offset_input.returnPressed.connect(self.on_lat_text_change)

        # Add the latitude slider, label, and input box to the horizontal layout
        lat_slider_layout.addWidget(lat_slider_label)
        lat_slider_layout.addWidget(self.lat_offset_slider)
        lat_slider_layout.addWidget(self.lat_offset_input)

        # Layout for longitude offset slider and its components
        lng_slider_layout = QHBoxLayout()
        lng_slider_label = QLabel("Lng Offset:")
        lng_slider_label.setFixedWidth(80)
        self.lng_offset_slider = QSlider(Qt.Horizontal)
        self.lng_offset_slider.setMinimum(-100)
        self.lng_offset_slider.setMaximum(100)
        self.lng_offset_slider.setValue(0)
        self.lng_offset_slider.valueChanged.connect(self.on_lng_slider_change)

        self.lng_offset_input = QLineEdit("0")
        self.lng_offset_input.setFixedWidth(40)
        self.lng_offset_input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lng_offset_input.returnPressed.connect(self.on_lng_text_change)

        # Add the longitude slider, label, and input box to the horizontal layout
        lng_slider_layout.addWidget(lng_slider_label)
        lng_slider_layout.addWidget(self.lng_offset_slider)
        lng_slider_layout.addWidget(self.lng_offset_input)

        # Add both horizontal slider layouts to the main vertical layout
        layout.addLayout(lat_slider_layout)
        layout.addLayout(lng_slider_layout)

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

    def save_map_with_input(self):
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

    def save_annotations(self):
        db = Database()
        coordinates = self.gl_widget.coordinates_stack
        markers = self.gl_widget.markers_stack
        for (tree_lat, tree_lng), (image_x, image_y) in zip(coordinates, markers):
            db.insert_annotation(
                image_path="/path/to/image.jpg",
                pano_id="pano_001",
                stview_lat=self.gl_widget.lat,
                stview_lng=self.gl_widget.lng,
                tree_lat=tree_lat,
                tree_lng=tree_lng,
                lat_offset=self.lat_offset,
                lng_offset=self.lng_offset,
                image_x=image_x,
                image_y=image_y,
                height=0,
                diameter=0,
            )
        db.close()

    def on_lat_slider_change(self):
        value = self.lat_offset_slider.value()
        delta = value - self.lat_offset
        self.lat_offset = value
        self.lat_offset_input.setText(str(value))
        self.update_map(delta, 0)

    def on_lng_slider_change(self):
        value = self.lng_offset_slider.value()
        delta = value - self.lng_offset
        self.lng_offset = value
        self.lng_offset_input.setText(str(value))
        self.update_map(0, delta)

    def on_lat_text_change(self):
        value = int(self.lat_offset_input.text())
        value = max(-100, min(100, value))
        self.lat_offset_slider.setValue(value)
        delta = value - self.lat_offset
        self.lat_offset = value
        self.update_map(delta, 0)

    def on_lng_text_change(self):
        value = int(self.lng_offset_input.text())
        value = max(-100, min(100, value))
        self.lng_offset_slider.setValue(value)
        delta = value - self.lng_offset
        self.lng_offset = value
        self.update_map(0, delta)

    def update_map(self, lat, lng):
        update_script = f"updateMap({lat}, {lng});"
        self.findChild(QWebEngineView).page().runJavaScript(update_script)

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
