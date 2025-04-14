import base64
import os

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image, ImageDraw
from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtOpenGL import QGLWidget

from utils.processor import move_in_heading
from utils.utils import calculate


class GLWidget(QGLWidget):
    def __init__(self, parent, image, depth, heading, lat, lng, yaw, segmentation_mask=None):
        super().__init__(parent)
        self.window = parent

        self.setFocusPolicy(Qt.StrongFocus)

        self.lat, self.lng = lat, lng
        self.image = image
        self.original_image = image.copy()
        self.depth = depth
        self.image_width, self.image_height = self.image.size
        self.output_directory = "Output"
        self.yaw = yaw
        self.heading = heading
        self.pitch = 0
        self.prev_dx = 0
        self.prev_dy = 0
        self.fov = 90
        self.direction = 0
        self.moving = False
        self.segmentation_mask = segmentation_mask

        self.coordinates_stack = []
        self.markers_stack = []

        # self.sidebar_widget = sidebar_widget
        # street view params
        self.stroke_width = 25
        self.transparency = 50  # in range 0-100
        self.color = (255, 0, 0, 128)
        # map params
        self.map_color = (255, 0, 0, 128)
        self.map_transparency = 0.5  # in range 0-1
        self.map_color_name = "Red"

    def initializeGL(self):
        glEnable(GL_TEXTURE_2D)
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGB,
            self.image_width,
            self.image_height,
            0,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            self.image.tobytes(),
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        self.sphere = gluNewQuadric()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, self.width() / self.height(), 0.1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Street view rendering
        glPushMatrix()
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        glRotatef(90, 1, 0, 0)
        glRotatef(-90, 0, 0, 1)
        gluQuadricTexture(self.sphere, True)
        gluSphere(self.sphere, 1, 100, 100)
        glPopMatrix()

        # draw the crosshair
        self.draw_crosshair()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.width() / self.height(), 0.1, 1000)
        glMatrixMode(GL_MODELVIEW)

    def keyPressEvent(self, event):
        speed = 3
        if event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_W:
            self.pitch = self.pitch - speed
        elif event.key() == QtCore.Qt.Key_Down or event.key() == QtCore.Qt.Key_S:
            self.pitch = self.pitch + speed
        elif event.key() == QtCore.Qt.Key_Left or event.key() == QtCore.Qt.Key_A:
            self.yaw = 360 if self.yaw <= 0 else self.yaw
            self.yaw = (self.yaw - speed) % 360
        elif event.key() == QtCore.Qt.Key_Right or event.key() == QtCore.Qt.Key_D:
            self.yaw = (self.yaw + speed) % 360
        elif event.key() == QtCore.Qt.Key_Z:
            (image_pixel_x, image_pixel_y) = self.markers_stack.pop()
            (lat, lng) = self.coordinates_stack.pop()
            self.erase_point(image_pixel_x, image_pixel_y)
            # self.sidebar_widget.update_coordinates_label()
        elif event.key() == QtCore.Qt.Key_J:
            lat, lng = move_in_heading(self.lat, self.lng, self.yaw + 180)
            self.window.get_panorama(lat, lng, self.yaw)
        self.update()
        self.moving = False

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
            self.moving = True
        elif event.button() == QtCore.Qt.RightButton:
            self.handle_right_button_press(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.moving = False

    def handle_right_button_press(self, event):
        self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()

        distance, self.direction, image_pixel_x, image_pixel_y, depth = calculate(
            self.mouse_x,
            self.mouse_y,
            self.yaw,
            self.pitch,
            self.depth,
            self.image_width,
            self.image_height,
            self.width(),
            self.height(),
            self.heading,
        )

        if depth > 0 and distance > 0:
            print(
                f"depth = {depth}, Distance = {distance}, Heading = {self.heading}, Direction = {int(self.direction)}"
            )
            lat, lng = move_in_heading(
                self.lat, self.lng, int(self.direction), distance / 1000
            )
            self.draw_point(image_pixel_x, image_pixel_y)
            self.markers_stack.append((image_pixel_x, image_pixel_y))
            self.coordinates_stack.append((lat, lng))
            # self.sidebar_widget.update_coordinates_label()
        else:
            print("Inf")

    def mouseMoveEvent(self, event):
        if self.segmentation_mask is not None:
            pixel_x, pixel_y = utils.screen_to_pixel_coordinates(
                    event.pos().x(), event.pos().y(),
                    self.image_width, self.image_height,
                    self.width(), self.height()
            )
            if 0 <= pixel_y < self.segmentation_mask.shape[0] and 0 <= pixel_x < self.segmentation_mask.shape[1]:
                segment_label = self.segmentation_mask[pixel_y, pixel_x]
                if segment_label != 0:
                    print(f"Hovering over segment: {segment_label}")

        if self.moving:
            center_x = self.width() // 2
            center_y = self.height() // 2
            dx = event.pos().x() - center_x
            dy = event.pos().y() - center_y
            dx *= 0.1
            dy *= 0.1
            self.yaw += dx
            self.pitch += dy
            if self.yaw >= 360:
                self.yaw %= 360
            elif self.yaw < 0:
                self.yaw = 360 + (self.yaw % 360)
            self.pitch = min(max(self.pitch, -90), 90)
            QCursor.setPos(self.mapToGlobal(QPoint(center_x, center_y)))
            self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.fov -= delta * 0.1
        self.fov = max(30, min(self.fov, 90))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.width() / self.height(), 0.1, 1000)
        self.update()

    def set_stroke_width(self, width):
        self.stroke_width = width
        self.update()

    def set_stroke_color(self, color):
        self.color = color
        self.update()

    def set_map_transparency(self, map_transparency):
        self.map_transparency = map_transparency
        self.update()

    def set_map_color(self, map_color, map_color_name):
        self.map_color = map_color
        self.map_color_name = map_color_name
        self.update()

    def draw_point(self, x, y):
        draw = ImageDraw.Draw(self.image, "RGBA")  # 'RGBA' for transparency
        half_size = self.stroke_width
        center = (x, y)
        radius = half_size
        point_color = self.color
        draw.ellipse(
            [
                (center[0] - radius, center[1] - radius),
                (center[0] + radius, center[1] + radius),
            ],
            fill=point_color,
        )
        glDeleteTextures(1, [self.texture])
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGB,
            self.image_width,
            self.image_height,
            0,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            self.image.tobytes(),
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        self.update()

    def erase_point(self, x, y):
        # Create a mask for the area to be erased
        mask = Image.new("L", self.image.size, 0)
        draw = ImageDraw.Draw(mask)
        half_size = self.stroke_width
        center = (x, y)
        radius = half_size
        draw.ellipse(
            [
                (center[0] - radius, center[1] - radius),
                (center[0] + radius, center[1] + radius),
            ],
            fill=255,
        )

        # Convert mask to numpy array
        mask_array = np.array(mask)

        # Get the original image data
        original_array = np.array(self.original_image)
        current_array = np.array(self.image)

        # Replace the area in the current image with the original image data
        current_array[mask_array == 255] = original_array[mask_array == 255]

        # Convert back to PIL Image
        self.image = Image.fromarray(current_array)

        # Update OpenGL texture
        glDeleteTextures(1, [self.texture])
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGB,
            self.image_width,
            self.image_height,
            0,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            self.image.tobytes(),
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        self.update()

    def save_image(self):
        """
        - Latitude
        - Longitude
        - Aerial (0) / Street-view (1)
        - Zoom Level (for aerial) / FOV (for street view)
        - Direction/Pitch (-1 for Aerial)
        - Yaw (-1 for Aerial)
        - Panorma (0) / Current-View (1) / Aerial View (-1)
        """
        filename = f"{self.lat},{self.lng},1,{self.fov},{self.pitch},{self.yaw},{0}"

        encoded_filename = base64.b64encode(filename.encode()).decode()
        full_path = os.path.join(self.output_directory, f"{encoded_filename}.png")
        self.image.save(full_path)
        print(f"Street-view Image saved")

    def draw_crosshair(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(-1, 1, -1, 1, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_TEXTURE_2D)
        glColor3f(1.0, 1.0, 1.0)  # White color
        glLineWidth(2.0)  # Set line width

        glBegin(GL_LINES)
        # Vertical line
        glVertex2f(0, 0.03)
        glVertex2f(0, -0.03)
        # Horizontal line
        glVertex2f(-0.05, 0)
        glVertex2f(0.05, 0)
        glEnd()

        glEnable(GL_TEXTURE_2D)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    # def draw_polygon(self, markers_stack):
    #
    #     draw = ImageDraw.Draw(self.image, "RGBA")  # 'RGBA' for transparency
    #     draw.polygon(markers_stack, self.color)
    #
    #     glDeleteTextures(1, [self.texture])
    #     self.texture = glGenTextures(1)
    #     glBindTexture(GL_TEXTURE_2D, self.texture)
    #     glTexImage2D(
    #         GL_TEXTURE_2D,
    #         0,
    #         GL_RGB,
    #         self.image_width,
    #         self.image_height,
    #         0,
    #         GL_RGB,
    #         GL_UNSIGNED_BYTE,
    #         self.image.tobytes(),
    #     )
    #     glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    #     glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    #     self.update()
