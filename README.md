# rmk2

## Overview

This package serves as a personal toolbox, gathering various functions that I keep
reaching for when working on various projects.

## Installation

This project is written in `python3`.

It uses `pipenv` for dependency management, `pytest` for testing, `black` for
formatting, and `pbr` for packaging.

### Python environment

To retrieve the full source code and initialise a local virtual environment including
required packages, run:

```
# Git
git clone https://gitlab.com/rmk2/rmk2-py.git

# Pipenv
# NB: with the switch -d, pipenv also installs development packages, such as pytest
pipenv install -d

# Activate environment
pipenv shell

# Optional: generate a requirements.txt via pipenv, which pbr uses to check dependencies
pipenv lock --requirements > requirements.txt

# Install locally checked out package
pip install -e .
```
