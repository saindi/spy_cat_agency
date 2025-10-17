#! /usr/bin/env bash
set -euxo pipefail

pip install pre-commit
pre-commit install
pre-commit run --all-files
