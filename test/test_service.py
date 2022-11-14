from itertools import product

import xml.etree.ElementTree as ET

from pytest_container import DerivedContainer
from pytest_container.container import ContainerData


_RPMS_DIR = "/src/rpms/"

_AAA_BASE_URL = "https://github.com/openSUSE/aaa_base"

CONTAINERFILE = f"""RUN zypper -n in python3 git build diff

RUN git config --global user.name "SUSE Bot" && \
    git config --global user.email "noreply@suse.com" && \
    git config --global protocol.file.allow always

RUN mkdir -p {_RPMS_DIR}ring0 && \
    cd {_RPMS_DIR} && git clone https://github.com/openSUSE/libeconf && \
    cd libeconf && git rev-parse HEAD > /src/libeconf && \
    cd {_RPMS_DIR}ring0 && \
    git init && git submodule add {_AAA_BASE_URL} && \
    git commit -m "add aaa_base" && \
    git submodule add ../libeconf && git commit -m "add libeconf" && \
    cd aaa_base && git rev-parse HEAD > /src/aaa_base

COPY obs_scm_bridge /usr/bin/
"""

TUMBLEWEED = DerivedContainer(
    base="registry.opensuse.org/opensuse/tumbleweed", containerfile=CONTAINERFILE
)
LEAP_15_3, LEAP_15_4 = (
    DerivedContainer(
        base=f"registry.opensuse.org/opensuse/leap:15.{ver}",
        containerfile=CONTAINERFILE,
    )
    for ver in (3, 4)
)
BCI_BASE_15_3, BCI_BASE_15_4 = (
    DerivedContainer(
        base=f"registry.suse.com/bci/bci-base:15.{ver}", containerfile=CONTAINERFILE
    )
    for ver in (3, 4)
)


CONTAINER_IMAGES = [TUMBLEWEED, LEAP_15_3, LEAP_15_4, BCI_BASE_15_3, BCI_BASE_15_4]


def test_service_help(auto_container: ContainerData):
    """This is just a simple smoke test to check whether the script works."""
    auto_container.connection.run_expect([0], "obs_scm_bridge --help")


def test_clones_the_repository(auto_container_per_test: ContainerData):
    """Check that the service clones the manually created repository correctly."""
    dest = "/tmp/ring0"
    auto_container_per_test.connection.run_expect(
        [0], f"obs_scm_bridge --outdir {dest} --url {_RPMS_DIR}ring0"
    )
    auto_container_per_test.connection.run_expect([0], f"diff {dest} {_RPMS_DIR}ring0")


def test_creates_packagelist(auto_container_per_test: ContainerData):
    """Smoke test for the generation of the package list files `$pkg_name.xml`
    and `$pkg_name.info`:

    - verify that the destination folder contains all expected `.info` and
      `.xml` files
    - check the `scmsync` elements in the `.xml` files
    - check the HEAD hashes in the `.info` files
    """
    dest = "/tmp/ring0"
    auto_container_per_test.connection.run_expect(
        [0], f"obs_scm_bridge --outdir {dest} --url {_RPMS_DIR}ring0 --projectmode 1"
    )
    libeconf_hash, aaa_base_hash = (
        auto_container_per_test.connection.file(
            f"/src/{pkg_name}"
        ).content_string.strip()
        for pkg_name in ("libeconf", "aaa_base")
    )

    files = auto_container_per_test.connection.file(dest).listdir()
    assert len(files) == 4
    for file_name in (
        f"{pkg}.{ext}"
        for pkg, ext in product(("aaa_base", "libeconf"), ("xml", "info"))
    ):
        assert file_name in files

    def _test_pkg_xml(pkg_name: str, expected_url: str, expected_head_hash: str):
        conf = ET.fromstring(
            auto_container_per_test.connection.file(
                f"{dest}/{pkg_name}.xml"
            ).content_string
        )
        assert conf.attrib["name"] == pkg_name
        scm_sync_elements = conf.findall("scmsync")
        assert len(scm_sync_elements) == 1 and scm_sync_elements[0].text
        assert f"{expected_url}#{expected_head_hash}" in scm_sync_elements[0].text

    _test_pkg_xml("aaa_base", _AAA_BASE_URL, aaa_base_hash)
    _test_pkg_xml("libeconf", f"{_RPMS_DIR}libeconf", libeconf_hash)

    for pkg_name, pkg_head_hash in (
        ("aaa_base", aaa_base_hash),
        ("libeconf", libeconf_hash),
    ):
        assert (
            pkg_head_hash
            == auto_container_per_test.connection.file(
                f"{dest}/{pkg_name}.info"
            ).content_string.strip()
        )
