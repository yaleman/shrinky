""" shrinky module """

import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

from loguru import logger
from PIL import Image

def parse_geometry(geometry_input: str) -> Tuple[Optional[int],Optional[int]]:
    """ parse the geometry provided """
    if "x" in geometry_input:
        x_value, y_value = geometry_input.split("x")
        if x_value == '':
            x_result = None
        else:
            x_result = int(x_value)

        if y_value == '':
            y_result = None
        else:
            y_result = int(y_value)
        return (x_result,y_result)
    return (0,0)

def new_filename(original_filename: Path) -> Path:
    """generates a new filename based on the path"""
    logger.debug("lol {}", original_filename)

    extension = get_extension(original_filename)
    basename = ".".join(original_filename.resolve().name.split(".")[:-1])
    newname = f"{basename}-shrink.{extension}"

    return Path(f"{original_filename.parent}/{newname}").resolve()

def get_extension(filename: Path) -> str:
    """ gets the file extension is a hacky way """
    if "." not in filename.name:
        raise ValueError("Can't have an extension when there's no dot!")
    return filename.resolve().name.split(".")[-1]

class ShrinkyImage:
    """ does all the things """

    def __init__(self, source_path: Path):
        """ loads the image """
        self.source_path = source_path
        self.image = Image.open(source_path.open('rb'))
        logger.debug("Dims: {}x{}", self.image.width, self.image.height)
        logger.info("Original file size: {}", os.stat(self.source_path.resolve()).st_size)

    def resize_image(
        self,
        new_width: int,
        new_height: int,
        source_image: Optional[Image.Image] = None,
        ) -> Image.Image:
        """ resizes an image, doesn't modify the source image """
        if source_image is None:
            source_image = self.image

        tmpimage = source_image.copy()

        if source_image.width > new_width or source_image.height > new_height:
            logger.debug(
                "Thumbnailing from {}x{} to {}x{}",
                source_image.width,
                source_image.height,
                new_width,
                new_height,
            )
            tmpimage.thumbnail((new_width, new_height))
        return tmpimage


    def write_image(self,
        output_filename: Path,
        force_overwrite: bool=False,
        quality: int=-1
        ) -> bool:
        """ writes the file to disk"""
        if output_filename.exists() and not force_overwrite:
            logger.error("{} already exists, bailing", output_filename.resolve())
            return False

        args: Dict[str, Union[str, int]] = {}

        if get_extension(output_filename).lower() in ("jpg", "jpeg"):
            # set jpeg quality
            if quality is not None and quality >= 0:
                args["quality"] = quality

            if self.image.mode != "RGB":
                self.image = self.image.convert("RGB")

        with output_filename.open('wb') as output_image:
            logger.info("Writing {}", output_image.name)
            self.image.save(
                output_image,
                **args #type: ignore
            )

        new_size = os.stat(output_filename.resolve()).st_size
        logger.info("New size: {}", new_size )
        return True
