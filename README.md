# Welcome to buda

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/ufuk-cakir/buda/ci.yml?branch=main)](https://github.com/ufuk-cakir/buda/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/buda/badge/)](https://buda.readthedocs.io/)
[![codecov](https://codecov.io/gh/ufuk-cakir/buda/branch/main/graph/badge.svg)](https://codecov.io/gh/ufuk-cakir/buda)

## Installation

The Python package `buda` can be installed by downloading this repo and then running the following:

```
pip install .
```

## Development installation

If you want to contribute to the development of `buda`, we recommend
the following editable installation from this repository:

```
git clone https://github.com/ufuk-cakir/buda.git
cd buda
python -m pip install --editable .[tests]
```

Having done so, the test suite can be run using `pytest`:

```
python -m pytest
```

## Acknowledgments

This repository was set up using the [SSC Cookiecutter for Python Packages](https://github.com/ssciwr/cookiecutter-python-package).
