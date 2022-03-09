""" CLI for shrinky """

from pathlib import Path
from typing import Optional

from loguru import logger

import click

from . import new_filename, ShrinkyImage

@click.command()
@click.argument("filename", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False, dir_okay=False, resolve_path=True, path_type=Path),
)
@click.option("-f", "--force", is_flag=True, help_text="Overwrite destination")
def cli(
    filename: Path = Path("~/"),
    output: Optional[Path]=None,
    force: bool = False
) -> bool:
    """Shrinky shrinks images in a way I like"""

    image_dimensions = (2000, 2000)

    if output is None:
        output = new_filename(filename)

    if output.exists() and not force:
        logger.error("{} already exists, bailing", output.resolve())

    original_file = Path(filename).resolve()
    if not original_file.exists():
        logger.error("Can't find {}, bailing", original_file)
        return False

    image = ShrinkyImage(original_file)

    image.resize_image(*image_dimensions)

    image.write_image(output)

    return True


if __name__ == "__main__":
    cli()
