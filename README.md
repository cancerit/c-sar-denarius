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

### Updating licence headers

Please use [skywalking-eyes](https://github.com/apache/skywalking-eyes).

Expected workflow:

1. Check state before modifying `.licenserc.yaml`:
   - `docker run -it --rm -v $(pwd):/github/workspace apache/skywalking-eyes header check`
   - You should get some 'valid' here, those without a header as 'invalid'
1. Modify `.licenserc.yaml`
1. Apply the changes:
   - `docker run -it --rm -v $(pwd):/github/workspace apache/skywalking-eyes header fix`
1. Add/commit changes

This is executed in the CI pipeline.

*DO NOT* edit the header in the files, please modify the date component of `content` in `.licenserc.yaml`.

If you need to make more extensive changes to the license carefully test the pattern is functional.
