/root/.local/bin/ruff check --fix .
/root/.local/bin/black --preview .
/root/.local/bin/isort --profile black .
/root/.local/bin/pyright
/root/.local/bin/pytest -v --ignore=vscode/bundled --ignore=benchmarks --ignore=benchmarks/benchmark_repos --ignore=testbed/exercism-python