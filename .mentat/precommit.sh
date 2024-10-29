ruff check --fix .
black --preview .
isort --profile black .
pyright
pytest