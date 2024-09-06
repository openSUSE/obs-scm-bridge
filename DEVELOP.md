
To execute the test suite locally, run:
```ShellSession
$ poetry run pytest -vv -x --pytest-container-log-level=debug
```

To run the tests in parallel, add the `-n auto` or `-n $nproc` parameter. To run only a specific test case, append the `-k $TEST_CASE_NAME` parameter.

