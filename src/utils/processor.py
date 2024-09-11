from math import asin, atan2, cos, degrees, radians, sin

import matplotlib.pyplot as plt
import numpy as np
from streetlevel import streetview


def get_panorama_id(lat, long):
    pano = streetview.find_panorama(lat, long, radius=500)
    if pano is None:
        return None
    return str(pano.id)


def move_in_heading(lat, lon, heading, distance=0.01):
    R = 6371.0
    heading_rad = radians(heading)

    lat_rad = radians(lat)
    lon_rad = radians(lon)

    new_lat_rad = asin(
        sin(lat_rad) * cos(distance / R)
        + cos(lat_rad) * sin(distance / R) * cos(heading_rad)
    )
    new_lon_rad = lon_rad + atan2(
        sin(heading_rad) * sin(distance / R) * cos(lat_rad),
        cos(distance / R) - sin(lat_rad) * sin(new_lat_rad),
    )
    new_lat = degrees(new_lat_rad)
    new_lon = degrees(new_lon_rad)

    return new_lat, new_lon


def download_panorama_image_and_depth(pano_id):
    pano = streetview.find_panorama_by_id(pano_id, download_depth=True)
    # panorama_path = f"data/Panormas/{pano.id}_panorma.jpg"
    panorma = streetview.get_panorama(pano, zoom=5)
    # streetview.download_panorama(pano, panorama_path, zoom=20)
    return panorma, pano


def save_depth_map(pano):
    depth_map_path = f"data/Depth_maps/numpy_depth.npy"
    np.save(depth_map_path, pano.depth.data)

    plt.imshow(pano.depth.data, cmap="viridis")
    plt.axis("off")
    depth_image_path = f"data/Depth_maps/depth_image.png"
    plt.savefig(depth_image_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()

    return pano.depth.data, depth_map_path, depth_image_path


def process_location(lat, long):
    pano_id = get_panorama_id(lat, long)
    if pano_id is None:
        return None, None, None, None, None
    panorma, pano = download_panorama_image_and_depth(pano_id)

    heading_degrees = degrees(pano.heading)
    print("Permalink:", pano.permalink(heading=heading_degrees, pitch=90))
    if pano.depth:
        depth_map, depth_map_path, depth_image_path = save_depth_map(pano)
    return panorma, depth_map, heading_degrees, pano.lat, pano.lon


# def generate_heading_pitch_arrays(pano_id, width=512, height=256, center_heading=0):
#     center_pixel_x = width // 2
#     center_pixel_y = height // 2

#     x_indices, y_indices = np.meshgrid(np.arange(width), np.arange(height))

#     headings = ((x_indices - center_pixel_x) / center_pixel_x) * 180.0
#     headings[x_indices < center_pixel_x] += 360
#     headings = (headings + center_heading) % 360

#     pitch_values = 180.0 * (y_indices / height)

#     heading_path = plot_heatmaps(pano_id, headings, pitch_values)

#     return headings, pitch_values, heading_path

# def plot_heatmaps(pano_id, headings, pitch_values):
#     plt.subplot(2, 1, 1)
#     plt.imshow(headings, cmap='viridis', aspect='auto', extent=[0, 512, 0, 256])
#     plt.colorbar(label='Heading (degrees)')
#     plt.title('Panorama Heading Heatmap')
#     plt.xlabel('Pixel Position (Horizontal)')
#     plt.ylabel('Pixel Position (Vertical)')

#     plt.subplot(2, 1, 2)
#     plt.imshow(pitch_values, cmap='viridis', aspect='auto', extent=[0, 512, 0, 256])
#     plt.colorbar(label='Pitch (degrees)')
#     plt.title('Panorama Pitch Heatmap')
#     plt.xlabel('Pixel Position (Horizontal)')
#     plt.ylabel('Pixel Position (Vertical)')

#     plt.tight_layout()
#     headings_path = f'data/Heading_and_pitch_maps/{pano_id}_heatmap_image.png'
#     plt.savefig(headings_path)
#     plt.close()
#     return headings_path
