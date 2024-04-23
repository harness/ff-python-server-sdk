python --version
python -m pip install --upgrade pip

python -m pip uninstall attr attrs
python -m pip install attrs

python -m pip install flake8 pytest coverage
python -m pip install -r requirements_dev.txt

make fmt
make lint
make dist
pytest --junitxml=junit.xml