""" testing shrinky things """

from pathlib import Path

from shrinky import new_filename

def test_new_filename():
    """ testing new fileanme """
    input_filename = Path("~/test.jpg").resolve()
    assert new_filename(input_filename) == Path("~/test-shrink.jpg").resolve()
