""" CLI for shrinky """

from pathlib import Path
from typing import Optional, Tuple

from loguru import logger

import click

from . import new_filename, parse_geometry, ShrinkyImage

DEFAULT_GEOMETRY = 2000


def set_geometry(geometry_value: Optional[str]) -> Tuple[int, int]:
    """geometry handler"""

    if geometry_value is None:
        return (DEFAULT_GEOMETRY, DEFAULT_GEOMETRY)

    max_x, max_y = parse_geometry(geometry_value)
    if max_x is None:
        max_x = DEFAULT_GEOMETRY
    if max_y is None:
        max_y = DEFAULT_GEOMETRY
    logger.debug("Setting geometry to {}x{}", max_x, max_y)
    return (max_x, max_y)


@click.command()
@click.argument("filename", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False, dir_okay=False, resolve_path=True, path_type=Path),
)
@click.option("-t", "--output-type", help="New file type (eg jpg, png etc")
@click.option("-g", "--geometry", help="Geometry, 1x1, 1x, x1 etc.")
@click.option("-q", "--quality", type=int, help="If JPEG, set quality.")
@click.option("-f", "--force", is_flag=True, help="Overwrite destination")
def cli(  # pylint: disable=too-many-arguments
    filename: Path = Path("~/"),
    output: Optional[Path] = None,
    output_type: Optional[str] = None,
    force: bool = False,
    quality: int = -1,
    geometry: Optional[str] = None,
) -> bool:
    """Shrinky shrinks images in a way I like"""

    image_dimensions = set_geometry(geometry_value=geometry)

    if output is None or output_type is not None:
        output = new_filename(filename, output_type)

    if output.exists() and not force:
        logger.error("{} already exists, bailing", output.resolve())

    original_file = Path(filename).resolve()
    if not original_file.exists():
        logger.error("Can't find {}, bailing", original_file)
        return False

    image = ShrinkyImage(original_file)

    # resize and store
    image.image = image.resize_image(*image_dimensions)

    image.write_image(
        output,
        force_overwrite=force,
        quality=quality,
    )

    return True


if __name__ == "__main__":
    cli() # type: ignore
    # TODO: wait for click to be re-typed to fix this
