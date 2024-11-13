import base64
import math
import os


def calculate_distance_and_direction(depth, pitch, yaw, heading):
    distance = depth * math.sin((180 - pitch) / 360)
    direction = yaw - 270 + heading
    if direction < 0:
        direction += 360
    return distance, direction


def calculate_image_pixel_coordinates(cal_yaw, cal_pitch, image_width, image_height):
    image_pixel_x = cal_yaw * (image_width / 360)
    image_pixel_y = cal_pitch * (image_height / 180)
    return image_pixel_x, image_pixel_y


def calculate_depth_indices(
    image_pixel_x, image_pixel_y, depth, image_width, image_height
):
    index_y = int(image_pixel_y * (depth.shape[0] / image_height))
    index_x = int(image_pixel_x * (depth.shape[1] / image_width)) * (-1)
    return depth[index_y][index_x]


def calculate(
    image_pixel_x,
    image_pixel_y,
    yaw,
    pitch,
    depth,
    image_width,
    image_height,
    heading,
):
    cal_pitch = (pitch + 90) % 180
    depth = calculate_depth_indices(
        image_pixel_x, image_pixel_y, depth, image_width, image_height
    )
    distance, direction = calculate_distance_and_direction(
        depth, cal_pitch, yaw, heading
    )

    return distance, direction, depth


def save_image(
    image, lat, lng, fov_zoom=90, pitch=0, yaw=0, street=False, folder_path="Output"
):
    """
    - Latitude
    - Longitude
    - Aerial (0) / Street-view (1)
    - Zoom Level (for aerial currently -1) / FOV (for street view)
    - Direction/Pitch (-1 for Aerial)
    - Yaw (-1 for Aerial)
    - Panorama (0) / Current-View (1) / Aerial View (-1)
    """
    if street:
        filename = f"{lat},{lng},1,{fov_zoom},{pitch},{yaw},{0}"
        encoded_filename = base64.b64encode(filename.encode()).decode()
        full_path = os.path.join(folder_path, f"{encoded_filename}.png")
        image.save(full_path)
        print(f"Street-view Image saved as PNG")
    else:
        filename = f"{lat},{lng},0,-1,-1,-1,-1"
        encoded_filename = base64.b64encode(filename.encode()).decode()
        full_path = os.path.join(folder_path, f"{encoded_filename}.png")

        image.grab().save(full_path)
        print(f"Map saved as PNG")
