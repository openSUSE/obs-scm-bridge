import os
import tempfile
import pytest
from obs_scm_bridge.manifest import read_project_manifest


class TestReadProjectManifest:
    def test_basic_manifest(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("packages:\n  - pkg1\n  - pkg2\nsubdirectories:\n  - subdir1\n")
            f.flush()
            try:
                packages, subdirs = read_project_manifest(f.name)
                assert packages == ['pkg1', 'pkg2']
                assert subdirs == ['subdir1']
            finally:
                os.unlink(f.name)

    def test_manifest_with_packages_only(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("packages:\n  - mypackage\n")
            f.flush()
            try:
                packages, subdirs = read_project_manifest(f.name)
                assert packages == ['mypackage']
                assert subdirs == []
            finally:
                os.unlink(f.name)

    def test_manifest_with_subdirs_only(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("subdirectories:\n  - dir1\n  - dir2\n")
            f.flush()
            try:
                packages, subdirs = read_project_manifest(f.name)
                assert packages == []
                assert subdirs == ['dir1', 'dir2']
            finally:
                os.unlink(f.name)

    def test_illegal_package_name_starts_with_dot(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("packages:\n  - .hidden\n  - valid_pkg\n")
            f.flush()
            try:
                packages, subdirs = read_project_manifest(f.name)
                assert packages == ['valid_pkg']
            finally:
                os.unlink(f.name)

    def test_illegal_package_name_starts_with_slash(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("packages:\n  - /invalid\n  - valid_pkg\n")
            f.flush()
            try:
                packages, subdirs = read_project_manifest(f.name)
                assert packages == ['valid_pkg']
            finally:
                os.unlink(f.name)

    def test_illegal_package_name_with_slash(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("packages:\n  - invalid/name\n  - valid_pkg\n")
            f.flush()
            try:
                packages, subdirs = read_project_manifest(f.name)
                assert packages == ['valid_pkg']
            finally:
                os.unlink(f.name)

    def test_illegal_package_name_with_asterisk(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("packages:\n  - wildcard*\n  - valid_pkg\n")
            f.flush()
            try:
                packages, subdirs = read_project_manifest(f.name)
                assert packages == ['valid_pkg']
            finally:
                os.unlink(f.name)

    def test_empty_manifest(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("\n")
            f.flush()
            try:
                packages, subdirs = read_project_manifest(f.name)
                assert packages is None
                assert subdirs == []
            finally:
                os.unlink(f.name)

    def test_no_packages_key(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("subdirectories:\n  - dir1\n")
            f.flush()
            try:
                packages, subdirs = read_project_manifest(f.name)
                assert packages is None
                assert subdirs == ['dir1']
            finally:
                os.unlink(f.name)
