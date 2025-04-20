# shrinky

[![PyPI](https://img.shields.io/pypi/v/shrinky.svg)](https://pypi.org/project/shrinky/)

Shrinks images in the way I want

## Installation

Install this library using `pip`:

    python -m pip install shrinky

## Usage

It's a CLI program, run `shrinky [OPTIONS] FILENAME`

    Options:
    -o, --output FILE
    -t, --output-type TEXT  New file type (eg jpg, png etc.)
    -g, --geometry TEXT     Resize to a maximum geometry, 1x1, 1x, x1 etc.
    -q, --quality INTEGER   If JPEG, set quality
    -f, --force             Overwrite destination
    --delete-source         Delete the source file once done
    -d, --debug             Enable debug logging
    --help                  Show this message and exit

For example, if you want to turn `example.png` to a JPEG file at quality 45, shrunk within an 800x800 bounding box, you can run:

`shrinky -t jpg -q 45 -g 800x00 example.png`

You'll end up with `example.jpg`.

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:

    cd shrinky
    uv run shrinky etc etc
