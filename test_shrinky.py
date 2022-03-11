""" testing shrinky things """

from pathlib import Path

from shrinky import new_filename, parse_geometry

def test_new_filename():
    """ testing new fileanme """
    input_filename = Path("~/test.jpg").resolve()
    assert new_filename(input_filename) == Path("~/test-shrink.jpg").resolve()

def test_parse_geometry():
    """ tests parse_geometry """

    testval = "800x800"
    result = parse_geometry(testval)
    assert result == (800,800)

    testval = "800x"
    result = parse_geometry(testval)
    assert result == (800,None)

    testval = "x800"
    result = parse_geometry(testval)
    assert result == (None,800)
