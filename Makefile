.PHONY: sync lint test check

sync:
	uv sync --frozen --group dev

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest -q

check: sync lint test
