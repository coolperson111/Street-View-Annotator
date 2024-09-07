import base64
import math
import os

# def get_new_coords(lat, lon, distance, direction):
#     earth_radius = 6378137  # meters
#
#     # Convert latitude and longitude from degrees to radians
#     lat_rad = radians(lat)
#     lon_rad = radians(lon)
#
#     # Convert direction from degrees to radians
#     direction_rad = radians(direction)
#
#     # Calculate new latitude
#     new_lat_rad = lat_rad + (distance / earth_radius) * cos(direction_rad)
#
#     # Calculate new longitude
#     new_lon_rad = lon_rad + (distance / earth_radius) * sin(direction_rad) / cos(
#         lat_rad
#     )
#
#     # Convert new latitude and longitude back to degrees
#     new_lat = degrees(new_lat_rad)
#     new_lon = degrees(new_lon_rad)
#
#     return new_lat, new_lon


def calculate_distance_and_direction(depth, cal_pitch, cal_yaw, heading):
    distance = depth * math.sin((180 - cal_pitch) / 360)
    direction = calculate_direction(cal_yaw, heading)
    return distance, direction


def screen_to_pixel_coordinates(
    mouse_x, mouse_y, image_width, image_height, width, height
):
    pixel_x = int(mouse_x / width * image_width)
    pixel_y = int((height - mouse_y) / height * image_height)
    return pixel_x, pixel_y


def calculate_image_pixel_coordinates(cal_yaw, cal_pitch, image_width, image_height):
    image_pixel_x = cal_yaw * (image_width / 360)
    image_pixel_y = cal_pitch * (image_height / 180)
    return image_pixel_x, image_pixel_y


def calculate_depth_indices(
    image_pixel_x, image_pixel_y, depth, image_width, image_height
):
    index_y = int(image_pixel_y * (depth.shape[0] / image_height))
    index_x = int(image_pixel_x * (depth.shape[1] / image_width)) * (-1)
    return index_y, index_x


def calculate_direction(yaw, heading):
    direction = yaw - 270 + heading
    if direction < 0:
        direction += 360
    return direction


def calculate(
    mouse_x,
    mouse_y,
    yaw,
    pitch,
    depth,
    image_width,
    image_height,
    width,
    height,
    heading,
):
    pixel_x, pixel_y = screen_to_pixel_coordinates(
        mouse_x, mouse_y, image_width, image_height, width, height
    )
    heading_offset = 0 - 270
    cal_yaw = (yaw - heading_offset) % 360
    cal_pitch = (pitch + 90) % 180
    image_pixel_x, image_pixel_y = calculate_image_pixel_coordinates(
        cal_yaw, cal_pitch, image_width, image_height
    )
    index_y, index_x = calculate_depth_indices(
        image_pixel_x, image_pixel_y, depth, image_width, image_height
    )
    depth = depth[index_y][index_x]

    distance, direction = calculate_distance_and_direction(
        depth, cal_pitch, cal_yaw, heading
    )

    return distance, direction, image_pixel_x, image_pixel_y, depth


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
