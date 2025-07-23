default:
    just --list

pytest:
    # Run tests using pytest
    uv run pytest

mypy:
    uv run mypy --strict shrinky tests

ruff:
    uv run ruff check shrinky tests

coverage:
    uv run coverage run -m pytest
    uv run coverage html --include='shrinky/*'
    open htmlcov/index.html

check: ruff mypy pytest