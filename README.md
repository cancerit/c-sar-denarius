# c-sar-denarius

Interface overlay for c-sar

## Development environment

This allows you to run all appropriate pre-commit tests.

### Python env

```bash
python3 -m venv venv
source venv/bin/activate

pip install -r tests/test-requirements.txt

# install pre-commit hooks
pip3 install pre-commit
pre-commit install

python setup.py develop # so bin scripts can find module
# If this is merged and pypi available move sauth into setup.py
# https://github.com/Granitosaurus/sauth/pull/1
pip install git+git://github.com/elfgoh/sauth.git@15dbca865332e7b83ccf5d9d227d0321a88132ca

# manually run pre-commit checks
pre-commit run -a
```
