from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget

from ui.map import FoliumWidget
# from ui.sidebar import SidebarWidget
from ui.streetview import GLWidget
from utils.sam_inference import run_sam_segmentation
from utils.processor import *


class MainWindow(QMainWindow):
    def __init__(self, lat, lng):
        super().__init__()
        self.setWindowTitle("Street View Annotator")
        self.setWindowIcon(QtGui.QIcon("assets/imgs/icon.png"))
        self.latitude, self.longitude = lat, lng
        self.panorama_id = None
        self.clipboard_lat, self.clipboard_lng = 30.71979998667062, 76.72142742674824
        (
            self.image,
            self.depth,
            self.heading,
            self.latitude,
            self.longitude,
            self.panorama_id,
        ) = process_location(
            self.latitude, self.longitude
        )

        if self.image:
            self.seg_map, self.masks = run_sam_segmentation(self.image)
        else:
            self.seg_map = None

        # comment for offline
        # self.heading = 0 # uncomment for offline
        # self.image = Image.open('assets/demo/demo_image.jpg') # uncomment for offline
        # self.depth = np.load('assets/demo/demo_depth.npy') # uncomment for offline
        # self.sidebar_widget = None
        self.folium_widget = None
        self.create_gl_widget()
        # self.sidebar_widget = SidebarWidget(self.gl_widget)
        # self.gl_widget.sidebar_widget = self.sidebar_widget
        self.folium_widget = FoliumWidget(self, self.gl_widget)
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_change)

        self.setup_ui()

    def setup_ui(self):
        self.central_layout = QHBoxLayout()
        # self.central_layout.addWidget(self.sidebar_widget)
        self.central_layout.addWidget(self.gl_widget, stretch=1)
        self.central_layout.addWidget(self.folium_widget, stretch=1)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.central_widget)

    def create_gl_widget(self, yaw=0):
        self.gl_widget = GLWidget(
            self,
            image=self.image,
            depth=self.depth,
            heading=self.heading,
            # sidebar_widget=None,
            lat=self.latitude,
            lng=self.longitude,
            yaw=yaw,
            segmentation_mask=self.seg_map #pass the seg_map here
        )
        # self.gl_widget.sidebar_widget = self.sidebar_widget
        # if self.folium_widget is not None and self.sidebar_widget is not None:
        #     self.folium_widget.gl_widget = self.gl_widget
        #     self.sidebar_widget.gl_widget = self.gl_widget
        if self.folium_widget is not None:
            self.folium_widget.gl_widget = self.gl_widget

    def get_panorama(self, lat=None, lng=None, yaw=0):
        if lat is None or lng is None:
            lat = self.clipboard_lat
            lng = self.clipboard_lng

        # if self.sidebar_widget:
        #     self.sidebar_widget.update_lat_lng(lat, lng)

        (
            self.image,
            self.depth,
            self.heading,
            self.latitude,
            self.longitude,
            self.panorama_id,
        ) = process_location(lat, lng)
        
        if self.image:
            self.seg_map, self.masks = run_sam_segmentation(self.image)
        else:
            self.seg_map = None

        if self.image is None:
            return

        self.update_position(lat, lng, yaw)

        self.central_layout.removeWidget(self.gl_widget)
        self.gl_widget.deleteLater()
        self.create_gl_widget(yaw=yaw)
        self.centralWidget().layout().insertWidget(0, self.gl_widget, stretch=1)
        self.folium_widget.markers.append((lat, lng))

    def update_position(self, lat, lng, yaw):
        self.folium_widget.findChild(QWebEngineView).page().runJavaScript(
            f"position({lat}, {lng}, {yaw+180});"
        )

    def on_clipboard_change(self):
        mime_data = self.clipboard.mimeData()

        if mime_data.hasText():
            clipboard_text = mime_data.text()
            try:
                self.clipboard_lat, self.clipboard_lng = eval(clipboard_text)
            except:
                pass
