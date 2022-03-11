# Building ff-python-server-sdk

This document shows the instructions on how to build and contribute to the SDK.

## Requirements

[Python >= 3.7](https://www.python.org/downloads/) or newer (python --version)<br>
[pip](https://packaging.python.org/en/latest/tutorials/installing-packages/#id12)<br>
<br>
[For Mac users](https://opensource.com/article/19/5/python-3-default-mac) if you don't already have pyenv or something similar installed for managing python version<br>


## Install Dependancies

```python
python -m pip install --upgrade pip
python -m pip install nose tornado flake8 pytest
python -m pip install -r requirements_dev.txt
```

## Build the SDK 
Some make targets have been provided to build and package the SDK

```bash
make dist
```

## Executing tests
pytest is used to run the SDK unit tests.

```python
pytest --junitxml=junit.xml
```

## Linting and Formating
To ensure the projecti is correctly formatted you can use the following commands
```bash
make lint fmt
```
