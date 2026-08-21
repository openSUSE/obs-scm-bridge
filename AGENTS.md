# Agent Guidelines

All code in Python modules within this repository must be compatible with Python 3.6 and later.
The main script obs_scm_bridge is used with a new python 3.13 and does not need compability
to older python versions.
When writing or modifying code:

- Use only features and syntax available since Python 3.6
- Avoid deprecated APIs (e.g., `ast.Str`, `ast.NameConstant`, `ast.Num` which were removed in Python 3.14)
- Use f-strings (available since 3.6)
- Use type hints from `typing` module (available since 3.5, but ensure compatibility)
- Prefer standard library over third-party when possible
- Test with the oldest supported Python version (3.6+) and with python3.13 use for the main script.

