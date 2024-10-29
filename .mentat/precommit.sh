black --preview .
isort --profile black .
ruff check --fix .
pyright
pytest