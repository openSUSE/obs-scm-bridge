
To execute the test suite locally, run:
```ShellSession
$ poetry run pytest -vv -x --pytest-container-log-level=debug
```

To run the tests in parallel, add the `-n auto` or `-n $nproc` parameter. To run only a specific test case, append the `-k $TEST_CASE_NAME` parameter.

The container based integration tests (test/test_service.py) require the
pytest-container dev dependency and a working docker. To run only the plain
unit tests, e.g. for the manifest parsing, run:
```ShellSession
$ poetry run pytest -vv test/test_manifest.py test/test_validate.py
```

