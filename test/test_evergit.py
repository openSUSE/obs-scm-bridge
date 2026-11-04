import os
import tempfile
import yaml
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import pytest

_loader = SourceFileLoader("obs_scm_bridge", "obs_scm_bridge")
_spec = spec_from_loader("obs_scm_bridge", _loader)
obs_scm_bridge_module = module_from_spec(_spec)
_loader.exec_module(obs_scm_bridge_module)
ObsGit = obs_scm_bridge_module.ObsGit


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Ensure clean environment for each test."""
    for key in ("OBS_SERVICE_PROJECT", "OBS_SERVICE_PACKAGE", "EVERGIT_URL", "EVERGIT_HOSTS", "GIT_CONFIG_PARAMETERS"):
        monkeypatch.delenv(key, raising=False)


def _create_temp_yaml(data):
    fd, path = tempfile.mkstemp(suffix=".yaml")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
    return path


def test_evergit_missing_file():
    obsgit = ObsGit(outdir="/tmp", url="https://example.com/repo.git", projectscmsync=None)
    obsgit.setup_evergit("/nonexistent/file.yaml")
    assert "GIT_CONFIG_PARAMETERS" not in os.environ


def test_evergit_invalid_yaml():
    fd, path = tempfile.mkstemp(suffix=".yaml")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("::not valid yaml::")
    try:
        obsgit = ObsGit(outdir="/tmp", url="https://example.com/repo.git", projectscmsync=None)
        obsgit.setup_evergit(path)
        assert "GIT_CONFIG_PARAMETERS" not in os.environ
    finally:
        os.unlink(path)


def test_evergit_targets_not_a_list():
    path = _create_temp_yaml({
        "url": "https://evergit.example.com",
        "targets": "not-a-list"
    })
    try:
        obsgit = ObsGit(outdir="/tmp", url="https://example.com/repo.git", projectscmsync=None)
        obsgit.setup_evergit(path)
        assert "GIT_CONFIG_PARAMETERS" not in os.environ
    finally:
        os.unlink(path)


def test_evergit_target_wildcard():
    path = _create_temp_yaml({
        "url": "https://evergit.example.com",
        "targets": ["*"]
    })
    try:
        obsgit = ObsGit(outdir="/tmp", url="https://example.com/repo.git", projectscmsync=None)
        obsgit.setup_evergit(path)
        assert "GIT_CONFIG_PARAMETERS" in os.environ
        git_params = os.environ["GIT_CONFIG_PARAMETERS"]
        assert "'url.https://evergit.example.com/github.com/.insteadOf=https://github.com/'" in git_params
        assert "'url.https://evergit.example.com/gitlab.com/.insteadOf=https://gitlab.com/'" in git_params
        assert "'url.https://evergit.example.com/bitbucket.org/.insteadOf=https://bitbucket.org/'" in git_params
    finally:
        os.unlink(path)


def test_evergit_target_project_match(monkeypatch):
    monkeypatch.setenv("OBS_SERVICE_PROJECT", "openSUSE:Factory")
    path = _create_temp_yaml({
        "url": "https://evergit.example.com",
        "targets": ["openSUSE:Factory"]
    })
    try:
        obsgit = ObsGit(outdir="/tmp", url="https://example.com/repo.git", projectscmsync=None)
        obsgit.setup_evergit(path)
        assert "GIT_CONFIG_PARAMETERS" in os.environ
    finally:
        os.unlink(path)


def test_evergit_target_subproject_requires_exact_match(monkeypatch):
    monkeypatch.setenv("OBS_SERVICE_PROJECT", "openSUSE:Factory:Live")
    path = _create_temp_yaml({
        "url": "https://evergit.example.com",
        "targets": ["openSUSE:Factory"]
    })
    try:
        obsgit = ObsGit(outdir="/tmp", url="https://example.com/repo.git", projectscmsync=None)
        obsgit.setup_evergit(path)
        assert "GIT_CONFIG_PARAMETERS" not in os.environ
    finally:
        os.unlink(path)


def test_evergit_target_project_mismatch(monkeypatch):
    monkeypatch.setenv("OBS_SERVICE_PROJECT", "home:user")
    path = _create_temp_yaml({
        "url": "https://evergit.example.com",
        "targets": ["openSUSE:Factory"]
    })
    try:
        obsgit = ObsGit(outdir="/tmp", url="https://example.com/repo.git", projectscmsync=None)
        obsgit.setup_evergit(path)
        assert "GIT_CONFIG_PARAMETERS" not in os.environ
    finally:
        os.unlink(path)


def test_evergit_target_project_and_package_match(monkeypatch):
    monkeypatch.setenv("OBS_SERVICE_PROJECT", "openSUSE:Factory")
    monkeypatch.setenv("OBS_SERVICE_PACKAGE", "libeconf")
    path = _create_temp_yaml({
        "url": "https://evergit.example.com",
        "targets": ["openSUSE:Factory/libeconf"]
    })
    try:
        obsgit = ObsGit(outdir="/tmp", url="https://example.com/repo.git", projectscmsync=None)
        obsgit.setup_evergit(path)
        assert "GIT_CONFIG_PARAMETERS" in os.environ
    finally:
        os.unlink(path)


def test_evergit_target_project_and_package_mismatch(monkeypatch):
    monkeypatch.setenv("OBS_SERVICE_PROJECT", "openSUSE:Factory")
    monkeypatch.setenv("OBS_SERVICE_PACKAGE", "otherpkg")
    path = _create_temp_yaml({
        "url": "https://evergit.example.com",
        "targets": ["openSUSE:Factory/libeconf"]
    })
    try:
        obsgit = ObsGit(outdir="/tmp", url="https://example.com/repo.git", projectscmsync=None)
        obsgit.setup_evergit(path)
        assert "GIT_CONFIG_PARAMETERS" not in os.environ
    finally:
        os.unlink(path)


def test_evergit_target_package_wildcard(monkeypatch):
    monkeypatch.setenv("OBS_SERVICE_PROJECT", "openSUSE:Factory")
    monkeypatch.setenv("OBS_SERVICE_PACKAGE", "anypkg")
    path = _create_temp_yaml({
        "url": "https://evergit.example.com",
        "targets": ["openSUSE:Factory/*"]
    })
    try:
        obsgit = ObsGit(outdir="/tmp", url="https://example.com/repo.git", projectscmsync=None)
        obsgit.setup_evergit(path)
        assert "GIT_CONFIG_PARAMETERS" in os.environ
    finally:
        os.unlink(path)


def test_evergit_custom_hosts():
    path = _create_temp_yaml({
        "url": "https://evergit.example.com",
        "hosts": ["git.mycompany.com"],
        "targets": ["*"]
    })
    try:
        obsgit = ObsGit(outdir="/tmp", url="https://example.com/repo.git", projectscmsync=None)
        obsgit.setup_evergit(path)
        git_params = os.environ.get("GIT_CONFIG_PARAMETERS", "")
        assert "git.mycompany.com" in git_params
        assert "github.com" not in git_params
    finally:
        os.unlink(path)


def test_evergit_existing_git_config_params(monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_PARAMETERS", "'user.name=Test'")
    path = _create_temp_yaml({
        "url": "https://evergit.example.com",
        "targets": ["*"]
    })
    try:
        obsgit = ObsGit(outdir="/tmp", url="https://example.com/repo.git", projectscmsync=None)
        obsgit.setup_evergit(path)
        git_params = os.environ.get("GIT_CONFIG_PARAMETERS", "")
        assert git_params.startswith("'user.name=Test'")
        assert "'url.https://evergit.example.com/github.com/.insteadOf=https://github.com/'" in git_params
    finally:
        os.unlink(path)


def test_evergit_missing_url_raises(monkeypatch):
    path = _create_temp_yaml({
        "targets": ["*"]
    })
    try:
        obsgit = ObsGit(outdir="/tmp", url="https://example.com/repo.git", projectscmsync=None)
        with pytest.raises(SystemExit):
            obsgit.setup_evergit(path)
    finally:
        os.unlink(path)


def test_run_cmd_nonfatal_preserves_git_config_parameters(monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_PARAMETERS", "'url.https://evergit.example.com/.insteadOf=https://github.com/'")
    obsgit = ObsGit(outdir="/tmp", url="https://example.com/repo.git", projectscmsync=None)
    custom_env = {"MY_VAR": "1"}
    rc, output = obsgit.run_cmd_nonfatal(["bash", "-c", "echo $GIT_CONFIG_PARAMETERS"], env=custom_env)
    assert rc == 0
    assert "'url.https://evergit.example.com/.insteadOf=https://github.com/'" in output
