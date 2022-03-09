""" shrinky module """

from pathlib import Path
from typing import Optional

from loguru import logger
from PIL import Image



def new_filename(original_filename: Path) -> Path:
    """generates a new filename based on the path"""
    logger.debug("lol {}", original_filename)

    shortname = original_filename.name
    if "." not in shortname:
        raise ValueError(f"No . in filename, can't work out extension: {shortname}")
    extension = shortname.split(".")[-1]
    basename = ".".join(shortname.split(".")[:-1])
    newname = f"{basename}-shrink.{extension}"

    return Path(f"{original_filename.parent}/{newname}").resolve()

class ShrinkyImage:
    """ does all the things """

    def __init__(self, source_path: Path):
        """ loads the image """
        self.source_path = source_path
        self.source_image = Image.open(source_path.open('rb'))
        logger.debug("Dims: {}x{}", self.source_image.width, self.source_image.height)


    def resize_image(
        self,
        new_width: int,
        new_height: int,
        source_image: Optional[Image.Image] = None,
        ) -> Image.Image:
        """ resizes an image, potentially recreates it from scratch"""
        if source_image is None:
            source_image = self.source_image

        if source_image.width > new_width or source_image.height > new_height:
            logger.debug(
                "Thumbnailing from {}x{} to {}x{}",
                source_image.width,
                source_image.height,
                new_width,
                new_height,
            )
            source_image.thumbnail((new_width, new_height))
        return source_image

    def write_image(self, new_filenmame: Path):
        """ writes the file to disk"""
        with new_filenmame.open('wb') as output_image:
            logger.info("Writing {}", output_image.name)
            self.source_image.save(
                output_image,
                self.source_image.format,
            )
