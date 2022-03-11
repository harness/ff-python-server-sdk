# Building ff-python-server-sdk

This document shows the instructions on how to build and execute the tests for this SDK.

Make sure that you have the Python version >= 3 with the “pip“
[https://pip.pypa.io/en/stable/installation/)][installed on your system], then run:

```
python -m pip install --upgrade pip
python -m pip install nose tornado flake8 pytest
python -m pip install -r requirements_dev.txt

make fmt
make lint
make dist
pytest
pytest --junitxml=junit.xml
```

This set of commands will build the SDK and run the tests.
