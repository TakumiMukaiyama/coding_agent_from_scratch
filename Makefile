init:
	uv sync -r uv.lock

test:
	uv run pytest -vv tests/

uv/create:
	uv venv

uv/install:
	uv install