# Publishing `mthreads-ml-py` to PyPI

```bash
# Build the distribution packages
python setup.py bdist_wheel
# Upload the packages to PyPI
python -m twine upload --repository pypi dist/*
```