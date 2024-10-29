/root/.local/bin/ruff check --fix .
/root/.local/bin/black --preview .
/root/.local/bin/isort --profile black .
/root/.local/bin/pyright
/root/.local/bin/pytest -v -W ignore::DeprecationWarning --ignore=vscode/bundled --ignore=benchmarks --ignore=tests/benchmarks --ignore=benchmarks/benchmark_repos --ignore=testbed/exercism-python