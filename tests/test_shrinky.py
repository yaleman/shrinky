"""testing shrinky things"""

from pathlib import Path
import pytest
from click.testing import CliRunner

from shrinky import (
    new_filename,
    parse_geometry,
    ShrinkyImage,
    cli,
    VALID_OUTPUT_TYPES,
    InvalidOutputType,
)

TEST_IMAGE_FILENAME = Path("tests/test_image.jpg").resolve()


def test_new_filename() -> None:
    """testing new fileanme"""
    input_filename = Path("~/test.jpg").resolve()
    assert new_filename(input_filename, None) == Path("~/test-shrink.jpg").resolve()


def test_new_filename_type() -> None:
    """testing new fileanme"""
    input_filename = Path("~/test.jpg").resolve()
    assert new_filename(input_filename, "png") == Path("~/test.png").resolve()


def test_new_filename_invalid() -> None:
    """testing new fileanme"""
    input_filename = Path("~/test.foo").resolve()
    with pytest.raises(InvalidOutputType):
        new_filename(input_filename, None)


def test_invalid_output_file() -> None:
    """tests the invalid output file exception"""
    shrinky = ShrinkyImage(TEST_IMAGE_FILENAME)
    with pytest.raises(ValueError):
        shrinky.write_image(Path("~/test-invalid").resolve())


def test_non_rgb_image(tmpdir: str) -> None:
    """tests the invalid output file exception"""
    shrinky = ShrinkyImage(TEST_IMAGE_FILENAME)
    shrinky.image = shrinky.image.convert(mode="RGBA")  # Convert to RGBA
    shrinky.write_image(Path(f"{tmpdir}/test-non-rgb.jpg"))


def test_parse_geometry() -> None:
    """tests parse_geometry"""

    testval = "800x800"
    result = parse_geometry(testval)
    assert result == (800, 800)

    testval = "800x"
    result = parse_geometry(testval)
    assert result == (800, None)

    testval = "x800"
    result = parse_geometry(testval)
    assert result == (None, 800)


def test_cli_bad_output_type() -> None:
    """tests the cli"""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        f"{TEST_IMAGE_FILENAME} -t helloworld",
    )

    assert result.exit_code == 1


def test_cli(tmpdir: str) -> None:
    """tests the cli"""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        f"{TEST_IMAGE_FILENAME} -o {tmpdir}/test.jpg -q 65 --debug",
    )

    assert result.exit_code == 0

    destfile = Path(f"{tmpdir}/test.jpg")
    assert destfile.exists()
    assert destfile.is_file()


def test_cli_geom(tmpdir: str) -> None:
    """tests the cli"""
    runner = CliRunner()  # capture stderr
    result = runner.invoke(
        cli,
        f"{TEST_IMAGE_FILENAME} -o {tmpdir}/test.jpg --debug -g 300x",
    )

    destfile = Path(f"{tmpdir}/test.jpg")
    assert destfile.exists()
    assert destfile.is_file()
    assert result.exit_code == 0


def test_cli_bad_geom(tmpdir: str) -> None:
    """tests the cli"""
    runner = CliRunner()  # capture stderr
    result = runner.invoke(
        cli,
        f"{TEST_IMAGE_FILENAME} -o {tmpdir}/test.jpg --debug -g 300",
    )

    destfile = Path(f"{tmpdir}/test.jpg")
    assert destfile.exists()
    assert destfile.is_file()
    assert result.exit_code == 0


def test_cli_bad_filename(tmpdir: str) -> None:
    """tests the cli"""
    runner = CliRunner()  # capture stderr
    test_filename = f"{tmpdir}/testdddd"
    print(f"{test_filename=}")
    testfile = Path(test_filename)
    testfile.touch()

    result = runner.invoke(
        cli,
        f"{test_filename} --debug -o {tmpdir}/test1234.derp",
    )
    print(result.stdout)
    assert result.exit_code == 1


def test_cli_missing_file(tmpdir: str) -> None:
    """tests the cli"""
    runner = CliRunner()  # capture stderr
    test_filename = f"{tmpdir}/testdddd1234"
    print(f"{test_filename=}")

    result = runner.invoke(
        cli,
        f"{test_filename}",
    )
    print(result.stdout)
    assert result.exit_code == 1


def test_cli_file_exists_bail(tmpdir: str) -> None:
    """tests the cli"""
    runner = CliRunner()  # capture stderr
    result = runner.invoke(
        cli,
        f"{TEST_IMAGE_FILENAME} -o {tmpdir}/test.jpg --debug -g 300x",
    )
    result = runner.invoke(
        cli,
        f"{TEST_IMAGE_FILENAME} -o {tmpdir}/test.jpg --debug -g 300x",
    )

    print(result.stdout)
    assert result.exit_code == 1
    assert result.exit_code == 1


def test_cli_file_write_weird_extension(tmpdir: str) -> None:
    """tests the cli"""
    runner = CliRunner()  # capture stderr
    result = runner.invoke(
        cli,
        f"{TEST_IMAGE_FILENAME} -o {tmpdir}/test --debug -g 300x",
    )

    print(result.stdout)
    assert result.exit_code == 1

    result = runner.invoke(
        cli,
        f"{TEST_IMAGE_FILENAME} -o {tmpdir}/test.exe --debug -g 300x",
    )
    print(result.stdout)
    assert result.exit_code == 1


def test_cli_file_write_variants(tmpdir: str) -> None:
    """tests the cli"""
    runner = CliRunner()  # capture stderr

    for extension in VALID_OUTPUT_TYPES:
        result = runner.invoke(
            cli,
            f"{TEST_IMAGE_FILENAME} -o {tmpdir}/test.{extension} --debug -g 300x",
        )
        print(result.stdout)
        assert result.exit_code == 0


def test_invalid_file(tmpdir: str) -> None:
    """tests the cli with an invalid file"""
    runner = CliRunner()  # capture stderr
    result = runner.invoke(
        cli,
        f"pyproject.toml --debug -o {tmpdir}/output.jpg",
    )
    print(result.stdout)
    assert result.exit_code == 1
