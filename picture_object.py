import math
from PIL import Image, ImageDraw
import numpy as np


class PictureObject:
    def __init__(self, data, masks_dir):
        self.name = data["nm"]
        self.type = data["type"]
        self.mask = self.generate_mask(data, masks_dir)
        self.area = self.mask.sum()

    @staticmethod
    def generate_mask(data, masks_dir):
        match data["shape"]:
            case "poly" if data.get("path") is not None:
                return PictureObject._mask_from_path(data["path"], data["image_size"])
            case "poly":
                return PictureObject._mask_from_png(f"{masks_dir}/{data['nm']}.png")
            case "bBox":
                return PictureObject._mask_from_bbox(data, data["image_size"])
            case _:
                raise ValueError(f"Unknown shape type: {data['shape']}")

    @staticmethod
    def _mask_from_path(path, image_size):
        img = Image.new("1", image_size, 0)
        points = [(x, y) for x, y in path[0]]
        ImageDraw.Draw(img).polygon(points, fill=1)
        return np.array(img)

    @staticmethod
    def _mask_from_png(mask_path):
        return np.array(Image.open(mask_path)) > 0

    @staticmethod
    def _mask_from_bbox(coords, image_size):
        width, height = image_size
        mask = np.zeros((height, width), dtype=bool)
        x1, y1 = max(0, math.floor(coords["x1"])), max(0, math.floor(coords["y1"]))
        x2, y2 = math.floor(coords["x2"]), math.floor(coords["y2"])
        mask[y1:y2, x1:x2] = True
        return mask
