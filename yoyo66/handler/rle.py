import os
import numpy as np
import json
from PIL import Image
from typing import List, TypeVar, Dict
import pycocotools.mask as mask_util

from yoyo66.handler import BaseFileHandler, mmfile_handler
from yoyo66.datastruct import phmImage, Layer

Array = TypeVar("Array", np.array)


@mmfile_handler("rle", ["json"])
class RLEFileHandler(BaseFileHandler):
    """
    RLE file handler for loading and saving pkg files (*.json).
    """

    __METRIC_KEY = "metric_"
    __ORIGINAL_LAYER = "Original"

    def __init__(self, filter: List[str] = None) -> None:
        super().__init__(filter)

    def _binary_mask_to_rle(self, binary_mask: Array) -> bytearray:
        """
        Checkout: https://cocodataset.org/#format-results
        :param mask [numpy.ndarray of shape (height, width)]: Decoded 2d segmentation mask

        This function returns the following dictionary:
        {
            "counts": encoded mask suggested by the official COCO dataset webpage.
            "size": the size of the input mask/image
        }
        """
        # Create dictionary for the segmentation key in the COCO dataset
        rle = {"counts": [], "size": list(binary_mask.shape)}
        # We need to convert it to a Fortran array
        binary_mask_fortran = np.asfortranarray(binary_mask, dtype=np.uint8)
        # Encode the mask as specified by the official COCO format
        encoded_mask = mask_util.encode(binary_mask_fortran)
        # We must decode the byte encoded string or otherwise we cannot save it as a JSON file
        rle["counts"] = encoded_mask["counts"].decode()
        return rle

    def _create_annotations(self, input: List[Layer], file_id: int) -> List[Dict]:
        annotations = []
        contour: Layer
        for id_, contour in enumerate(input):
            if contour.image.sum() == 0:
                continue
            # This function takes the image and fills the contour inside it.
            enc = self._binary_mask_to_rle(contour.image)
            seg = {
                "segmentation": enc,
                "area": int(np.sum(contour.image)),
                "image_id": file_id,
                "category_id": id_,
                "iscrowd": 0,
                "id": 0,
            }
            annotations.append(seg)

        return annotations

    def save(self, img: phmImage, filepath: str) -> None:
        """Save a multi-layer image as a tiff file

        Args:
            img (phmImage): Multi-layer image
            filepath (str): Path of tiff file
        """
        #  Save Original image
        metrics = {}
        for k, v in img.metrics.items():
            metrics[f"{self.__METRIC_KEY}{k}"] = v

        annotations = self._create_annotations(img.layers)
        metadata = {**img.properties, **metrics, "defects": img.layer_names}

        rle_file = {
            self.__ORIGINAL_LAYER: os.path.basename(filepath),
            "metadata": metadata,
            "annotations": annotations,
        }
        with open(filepath, "w") as fid:
            json.dump(rle_file, fid)

    def load(self, filepath: str) -> phmImage:
        """Load the multi-layer image using the presented file path (json file).

        Args:
            filepath (str): The path to an rle file
            Note: The original image must be in the same path as the rle file
        Returns:
            phmImage: Loaded multi-layer image
        """

        orig_img = None
        properties = {}
        metrics = {}
        layers = []
        with open(filepath, "r") as rle_fid:
            rle_file = json.load(rle_fid)

        if imgpath := rle_file.get(self.__ORIGINAL_LAYER, False):
            raise ValueError("Original image path not in rle file.")
        else:
            imgpath = os.path.join(os.path.pardir(filepath), imgpath)
            orig_img = np.array(Image.open(imgpath))

        metadata = rle_file.get("metadata", {})
        for key, value in metadata.items():
            if key.startswith(self.__METRIC_STARTKEY):
                metrics[key.replace(self.__METRIC_STARTKEY, "")] = value
            else:
                properties[key] = value

        for layer_name, ann in zip(
            rle_file["metadata"]["defects"], rle_file["annotations"]
        ):
            layers.append(
                Layer(
                    name=layer_name,
                    class_id=ann["category_id"],
                    image=mask_util.decode(ann["segmentation"]),
                )
            )

        return phmImage(
            filepath=filepath,
            properties=properties,
            orig_image=orig_img,
            layers=layers,
            metrics=metrics,
        )
