"""shrinky module"""

import os
from pathlib import Path
import sys
from typing import Any, Dict, Optional, Tuple, Union

import click
from loguru import logger
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener  # type: ignore[import-untyped]

register_heif_opener()

DEFAULT_GEOMETRY = 2000

VALID_OUTPUT_TYPES = [
    "jpg",
    "png",
    "gif",
    "webp",
    "avif",
    "heic",
    "heif",
]


def parse_geometry(geometry_input: str) -> Tuple[Optional[int], Optional[int]]:
    """parse the geometry provided"""
    if "x" in geometry_input:
        x_value, y_value = geometry_input.split("x")
        if x_value == "":
            x_result = None
        else:
            x_result = int(x_value)

        if y_value == "":
            y_result = None
        else:
            y_result = int(y_value)
        return (x_result, y_result)
    return (None, None)


def set_geometry(geometry_value: Optional[str]) -> Tuple[int, int]:
    """geometry handler"""

    if geometry_value is None:
        return (DEFAULT_GEOMETRY, DEFAULT_GEOMETRY)

    max_x, max_y = parse_geometry(geometry_value)
    if max_x is None or max_x == 0:
        max_x = DEFAULT_GEOMETRY
    if max_y is None or max_y == 0:
        max_y = DEFAULT_GEOMETRY
    logger.debug("Setting geometry to {}x{}", max_x, max_y)
    return (max_x, max_y)


class InvalidOutputType(Exception):
    """raised when the output type is invalid"""

    def __init__(self, output_type: str) -> None:
        super().__init__(
            f"Invalid output type: {output_type}, valid types are: {VALID_OUTPUT_TYPES}"
        )
        self.output_type = output_type


def new_filename(original_filename: Path, output_type: Optional[str]) -> Path:
    """generates a new filename based on the path"""
    logger.debug(f"{original_filename=}")

    basename = ".".join(original_filename.resolve().name.split(".")[:-1])
    if output_type is not None:
        logger.debug("Setting output type to {}", output_type.lower())
        newname = f"{basename}.{output_type.lower()}"
    else:
        try:
            extension = get_extension(original_filename)
            if extension.lower() not in VALID_OUTPUT_TYPES:
                raise InvalidOutputType(extension)
            newname = f"{basename}-shrink.{extension}"
        except ValueError:
            newname = f"{basename}-shrink.jpg"
            logger.error(
                "Can't get extension for {}, setting to {}", original_filename, newname
            )

    return Path(f"{original_filename.parent}/{newname}").resolve()


def get_extension(filename: Path) -> str:
    """gets the file extension is a hacky way"""
    if "." not in filename.name:
        raise ValueError("Can't have an extension when there's no dot!")
    return filename.resolve().name.split(".")[-1]


class ShrinkyImage:
    """does all the things"""

    def __init__(self, source_path: Path) -> None:
        """loads the image"""
        self.source_path = source_path
        try:
            self.image = Image.open(source_path.open("rb"))
        except UnidentifiedImageError as image_error:
            logger.error("Pillow can't handle the file '{}', bailing.", source_path)
            logger.error(image_error)
            raise image_error

        logger.debug("Dims: {}x{}", self.image.width, self.image.height)
        logger.info(
            "Original file size: {}", os.stat(self.source_path.resolve()).st_size
        )

    def resize_image(
        self,
        new_width: int,
        new_height: int,
        source_image: Optional[Image.Image] = None,
    ) -> Image.Image:
        """resizes an image, doesn't modify the source image"""
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

    def write_image(self, output_filename: Path, quality: int = -1) -> bool:
        """writes the file to disk"""

        try:
            file_extension = get_extension(output_filename).lower()
        except ValueError as extension_error:
            logger.error(extension_error)
            raise extension_error

        args: Dict[str, Union[str, int]] = {}

        if file_extension in ("jpg", "jpeg"):
            # set jpeg quality
            if quality is not None and quality >= 0:
                args["quality"] = quality

            if self.image.mode != "RGB":
                logger.debug("Image is not RGB: {}", self.image.mode)
                self.image = self.image.convert("RGB")

        with output_filename.open("wb") as output_image:
            logger.info("Writing {}", output_image.name)
            self.image.save(output_image, **args)  # type: ignore

        new_size = os.stat(output_filename.resolve()).st_size
        logger.info("New size: {}", new_size)
        return True


def setup_logging(
    logger_object: Any,
    debug: bool,
) -> None:
    """sets up loguru"""
    logger_object.remove()
    format_string = "<level>{level: <8}</level> - <level>{message}</level>"
    if debug:
        level = "DEBUG"

    else:
        level = "INFO"
    logger_object.add(sink=sys.stdout, format=format_string, level=level)


@click.command()
@click.argument("filename", type=click.Path(exists=False, path_type=Path))
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False, dir_okay=False, resolve_path=True, path_type=Path),
)
@click.option("-t", "--output-type", help="New file type (eg jpg, png avif etc)")
@click.option("-g", "--geometry", help="Geometry, 1x1, 1x, x1 etc.")
@click.option("-q", "--quality", type=int, help="If JPEG, set quality.")
@click.option("-f", "--force", is_flag=True, help="Overwrite destination")
@click.option(
    "--delete-source",
    is_flag=True,
    default=False,
    help="Delete the source file once done",
)
@click.option("--debug", "-d", is_flag=True, help="Enable debug logging")
def cli(
    filename: Path = Path("~/"),
    output: Optional[Path] = None,
    output_type: Optional[str] = None,
    force: bool = False,
    quality: int = -1,
    geometry: Optional[str] = None,
    delete_source: bool = False,
    debug: bool = False,
) -> bool:
    """Shrinky shrinks images in a way I like"""

    setup_logging(logger, debug)

    image_dimensions = set_geometry(geometry_value=geometry)

    if output_type is not None:
        if output_type.lower() not in VALID_OUTPUT_TYPES:
            logger.error(
                "Invalid output type {}, valid types are: {}",
                output_type,
                VALID_OUTPUT_TYPES,
            )
            sys.exit(1)
        else:
            logger.debug("Output type is {}", output_type.lower())

    if output is None or output_type is not None:
        output = new_filename(filename, output_type)

    if output.exists() and not force:
        logger.error("{} already exists, bailing", output.resolve())
        sys.exit(1)

    if get_extension(output).lower() not in VALID_OUTPUT_TYPES:
        logger.error(
            "Invalid output type {}, valid types are: {}",
            get_extension(output),
            VALID_OUTPUT_TYPES,
        )
        sys.exit(1)

    original_file = Path(filename).resolve()
    if not original_file.exists():
        logger.error("Can't find {}, bailing", original_file)
        sys.exit(1)

    # hacky workaround for the avif extension - https://github.com/python-pillow/Pillow/pull/5201
    if (
        get_extension(output).lower() == "avif"
        and "avif" not in Image.registered_extensions()
    ):
        import pillow_avif  # type: ignore  # noqa: F401,unused-import,import-outside-toplevel

    image = ShrinkyImage(original_file)

    # resize and store
    image.image = image.resize_image(*image_dimensions)

    image.write_image(
        output,
        quality=quality,
    )

    if delete_source:
        logger.info("Please confirm you want to remove {} (y/N):", original_file)
        if input().strip().lower() == "y":
            original_file.unlink()
            logger.info("Deleted {}", original_file)
        else:
            logger.info("Cancelled at user's request.")
    return True
