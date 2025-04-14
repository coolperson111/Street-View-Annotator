import numpy as np
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
from PIL import Image
import torch
import os

def run_sam_segmentation(pil_image):
    model_type = "vit_h"
    checkpoint_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'sam_vit_h.pth'))

    sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
    sam.to("cpu").eval()  # CPU inference since no GPU
    mask_generator = SamAutomaticMaskGenerator(sam)

    image_np = np.array(pil_image.convert("RGB"))

    # Convert the numpy array to a PyTorch tensor with the correct dtype
    image_tensor = torch.as_tensor(image_np, dtype=torch.uint8)  # Ensure the dtype is compatible
    image_tensor = image_tensor.permute(2, 0, 1)  # Convert from HWC to CHW format (as expected by PyTorch)

    masks = mask_generator.generate(image_np)

    seg_map = np.zeros(image_np.shape[:2], dtype=np.uint16)
    for idx, mask in enumerate(masks):
        seg_map[mask["segmentation"]] = idx + 1  # label each region

    return seg_map, masks
