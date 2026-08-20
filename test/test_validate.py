import os

from scm_bridge.project import ProjectScanner


def test_manifest():
    directory = "example"
    scanner = ProjectScanner(directory)
    packages, subdirectories = scanner.read_project_manifest(os.path.join(directory, "_manifest"))
    assert packages == []
    assert subdirectories == ["pkg/a", "pkg/b", "pkg/lib"]