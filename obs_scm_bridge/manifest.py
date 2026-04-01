import logging
import os
import re
import yaml
import configparser
from typing import Dict, List, Optional, Tuple


def read_project_manifest(filename: str) -> Tuple[Optional[List[str]], List[str]]:
    packages = None
    subdirectories = []
    manifest_yml = None
    with open(filename) as stream:
        manifest_yml = yaml.safe_load(stream)
    if 'packages' in manifest_yml:
        packages = []
    if manifest_yml.get('packages'):
        for name in manifest_yml['packages']:
            if not name or name.startswith('.') or name.startswith('/'):
                logging.warn("illegal packages entry '%s'", name)
                continue
            if '/' in name or '*' in name:
                logging.warn("packages entry with '/' or '*' not implemented yet")
                continue
            packages.append(name)
    if manifest_yml.get('subdirectories'):
        for newsubdir in manifest_yml['subdirectories']:
            if newsubdir:
                subdirectories.append(newsubdir)
    return packages, subdirectories

### Legacy, don't use this anymore
def read_project_subdirs(filename: str) -> Tuple[Optional[List[str]], List[str]]:
    packages = None
    subdirectories = []
    subdir_yml = None
    with open(filename) as stream:
        subdir_yml = yaml.safe_load(stream)
    for newsubdir in subdir_yml['subdirs']:
        if newsubdir:
            subdirectories.append(newsubdir)
    if 'toplevel' not in subdir_yml or subdir_yml['toplevel'] != 'include':
        packages = []
    return packages, subdirectories


_REGEXP = re.compile(r"^[a-zA-Z0-9\-\_\+][a-zA-Z0-9\.\-\_\+]*$")


def _read_gitmodules(directory: str) -> Dict[str, Tuple[str, str]]:
    submodule_paths = {}
    gitmodules_path = os.path.join(directory, '.gitmodules')
    if not os.path.isfile(gitmodules_path):
        return submodule_paths
    
    gsmconfig = configparser.ConfigParser()
    gitmodules = None
    with open(gitmodules_path) as f:
        gitmodules = f.read()
    gitmodules = "\n".join([line.lstrip() for line in gitmodules.split("\n")])
    gsmconfig.read_string(gitmodules)
    for section in gsmconfig.sections():
        gsm = gsmconfig[section]
        if 'path' in gsm:
            submodule_paths[gsm['path']] = (section, gsm.get('url', ''))
    return submodule_paths


def list_packages(directory: str) -> List[Tuple[str, str, Optional[str]]]:
    results = []
    seen = set()

    if not os.path.isdir(directory):
        return results

    submodule_paths = _read_gitmodules(directory)

    if os.path.isfile(directory + '/_manifest'):
        (_packages, _subdirs) = read_project_manifest(directory + '/_manifest')
        if _packages:
            for pkg in _packages:
                if not pkg or pkg.startswith('.'):
                    logging.warn("illegal packages entry '%s'", pkg)
                    continue
                if pkg in seen:
                    logging.debug("duplicate package entry '%s'", pkg)
                    continue
                seen.add(pkg)
                if '/' in pkg:
                    subdir = pkg
                    pkg_name = pkg.rsplit('/', 1)[-1]
                    results.append((pkg_name, subdir, None))
                else:
                    results.append((pkg, pkg, None))
        if _subdirs:
            for subdir in _subdirs:
                if not subdir:
                    continue
                if subdir in seen:
                    logging.debug("duplicate subdirectory entry '%s'", subdir)
                    continue
                seen.add(subdir)

                subdir_path = os.path.join(directory, subdir)
                if os.path.isdir(subdir_path):
                    for entry in os.listdir(subdir_path):
                        entry_path = os.path.join(subdir_path, entry)
                        if not os.path.isdir(entry_path):
                            continue
                        if not _REGEXP.match(entry):
                            continue
                        if entry in seen:
                            logging.debug("duplicate package entry '%s'", entry)
                            continue
                        seen.add(entry)
                        full_subdir = subdir + '/' + entry
                        submod_info = submodule_paths.get(full_subdir)
                        submod_url = submod_info[1] if submod_info else None
                        results.append((entry, full_subdir, submod_url))
                else:
                    submod_info = submodule_paths.get(subdir)
                    submod_url = submod_info[1] if submod_info else None
                    results.append((subdir, subdir, submod_url))
        return results

    ### legacy, might get dropped
    if os.path.isfile(directory + '/_subdirs'):
        (_packages, _subdirs) = read_project_subdirs(directory + '/_subdirs')
        if _packages:
            for pkg in _packages:
                if not pkg or pkg.startswith('.'):
                    logging.warn("illegal packages entry '%s'", pkg)
                    continue
                if pkg in seen:
                    logging.debug("duplicate package entry '%s'", pkg)
                    continue
                seen.add(pkg)
                if '/' in pkg:
                    subdir = pkg
                    pkg_name = pkg.rsplit('/', 1)[-1]
                    results.append((pkg_name, subdir, None))
                else:
                    results.append((pkg, pkg, None))
        if _subdirs:
            for subdir in _subdirs:
                if not subdir:
                    continue
                if subdir in seen:
                    logging.debug("duplicate subdirectory entry '%s'", subdir)
                    continue
                seen.add(subdir)

                subdir_path = os.path.join(directory, subdir)
                if os.path.isdir(subdir_path):
                    for entry in os.listdir(subdir_path):
                        entry_path = os.path.join(subdir_path, entry)
                        if not os.path.isdir(entry_path):
                            continue
                        if not _REGEXP.match(entry):
                            continue
                        if entry in seen:
                            logging.debug("duplicate package entry '%s'", entry)
                            continue
                        seen.add(entry)
                        full_subdir = subdir + '/' + entry
                        submod_info = submodule_paths.get(full_subdir)
                        submod_url = submod_info[1] if submod_info else None
                        results.append((entry, full_subdir, submod_url))
                else:
                    submod_info = submodule_paths.get(subdir)
                    submod_url = submod_info[1] if submod_info else None
                    results.append((subdir, subdir, submod_url))
        return results

    package_names = []
    subdirectory_names = []
    for entry in os.listdir(directory):
        if entry.startswith('.') or entry.startswith('/'):
            continue
        if not _REGEXP.match(entry):
            continue
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            subdirectory_names.append(entry)
        elif os.path.isfile(full_path):
            package_names.append(entry)

    for pkg in package_names:
        if pkg in seen:
            logging.debug("duplicate package entry '%s'", pkg)
            continue
        seen.add(pkg)
        results.append((pkg, pkg, None))
    for subdir in subdirectory_names:
        if subdir in seen:
            logging.debug("duplicate subdirectory entry '%s'", subdir)
            continue
        seen.add(subdir)
        submod_info = submodule_paths.get(subdir)
        submod_url = submod_info[1] if submod_info else None
        results.append((subdir, subdir, submod_url))

    for submod_path in submodule_paths.keys():
        if submod_path in seen:
            logging.debug("duplicate submodule entry '%s'", submod_path)
            continue
        seen.add(submod_path)
        submod_info = submodule_paths.get(submod_path)
        submod_url = submod_info[1] if submod_info else None
        results.append((submod_path, submod_path, submod_url))

    validated_results = []
    for pkg, subdir, submod in results:
        if not pkg and not subdir:
            logging.warn("entry has empty package_name and git_subdirectory")
            continue
        validated_results.append((pkg, subdir, submod))

    return validated_results
