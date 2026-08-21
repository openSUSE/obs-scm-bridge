# scm_bridge/project.py
# Scanning of a git clone for OBS packages and package containers.
#
# This module must stay compatible with Python 3.6 and later.

import configparser
import logging
import os
import sys

import yaml


class ProjectScanner(object):
    """Scan a git clone directory for OBS packages and package containers."""

    def __init__(self, directory):
        self.directory = directory
        self.processed = {}
        self.gsmpath = self._parse_gitmodules(directory)

    @staticmethod
    def _parse_gitmodules(directory):
        gsmpath = {}
        filename = os.path.join(directory, '.gitmodules')
        if not os.path.isfile(filename):
            return gsmpath

        # the parser stumbles over a mix of space and tabs. So, let's strip
        # leading whitespaces first
        with open(filename) as f:
            gitmodules = f.read()
        gitmodules = "\n".join([line.lstrip() for line in gitmodules.split("\n")])

        gsmconfig = configparser.ConfigParser()
        gsmconfig.read_string(gitmodules)
        for section in gsmconfig.sections():
            config = gsmconfig[section]
            if 'path' not in config:
                logging.warning("path not defined for git submodule " + section)
                continue
            path = config['path']
            if path in gsmpath:
                logging.warning("multiple definitions of %s path in git submodule config", path)
                continue
            gsmpath[path] = (section, config)
        return gsmpath

    def _die(self, msg):
        logging.error(msg)
        sys.exit(1)

    def _verify_subdir(self, subdir):
        if subdir.startswith('-'):
            self._die(f"illegal sub-directory '{subdir}'")

    def _check_subdir(self, subdir):
        fromdir = os.path.join(self.directory, subdir)
        if not os.path.realpath(fromdir + '/').startswith(os.path.realpath(self.directory + '/')):
            self._die(f"subdir {subdir} is not below clone directory")
        if not os.path.isdir(fromdir):
            self._die(f"subdir {subdir} does not exist")

    def list_packages(self, subdir=''):
        result = []
        if subdir:
            self._verify_subdir(subdir)
            self._check_subdir(subdir)
            subdir = subdir.rstrip('/') + '/'  # make sure subdir ends with a slash
        directory = (self.directory + '/' + subdir).rstrip('/')
        logging.debug("check %s (subdir=%s)", directory, subdir)

        if '_config' not in self.processed and os.path.isfile(directory + '/_config'):
            result.append(('_config', subdir + '_config', 'config', None))
            self.processed['_config'] = True

        packages = None
        subdirectories = []

        if os.path.isfile(directory + '/_manifest'):
            (packages, subdirectories) = self.read_project_manifest(directory + '/_manifest')
        elif os.path.isfile(directory + '/_subdirs'):
            (packages, subdirectories) = self.read_project_subdirs(directory + '/_subdirs')

        # handle all subdirectories
        for newsubdir in subdirectories:
            if (subdir + newsubdir + '/') in self.processed:
                continue
            self.processed[subdir + newsubdir + '/'] = True
            result += self.list_packages(subdir + newsubdir + '/')

        if packages is None:
            logging.debug("walk via %s", directory)
            packages = sorted(os.listdir(directory))

        # handle plain files and directories
        for name in packages:
            if name[0] == '.':
                continue
            if name in self.processed:
                continue                # already handled
            fname = directory + '/' + name
            if os.path.islink(fname):
                target = os.readlink(fname).rstrip('/')  # this is no recursive lookup, but is there a usecase?
                if not target or '/' in target or target.startswith('.'):
                    logging.warning("only local links are supported, skipping: %s -> %s", name, target)
                    continue
                if not os.path.isdir(directory + '/' + target):
                    logging.debug("skipping dangling symlink %s -> %s", name, target)
                    continue
                result.append((name, subdir + name, 'link', target))
                self.processed[name] = True
            elif os.path.isdir(fname):
                if (subdir + name + '/') in self.processed:
                    continue            # already handled in _subdir loop
                if (subdir + name) in self.gsmpath:
                    result.append((name, subdir + name, 'submodule', self.gsmpath[subdir + name]))
                else:
                    result.append((name, subdir + name, 'subdirectory', None))
                self.processed[name] = True

        return result

    def read_project_manifest(self, filename):
        packages = None
        subdirectories = []
        manifest_yml = None
        directory = os.path.dirname(filename)
        with open(filename) as stream:
            manifest_yml = yaml.safe_load(stream)

        if manifest_yml is None:
            # allowing an empty _manifest file
            return packages, subdirectories

        if 'packages' in manifest_yml:
            packages = []
        if manifest_yml.get('packages'):
            for name in manifest_yml['packages']:
                if not name or name.startswith('.') or name.startswith('/'):
                    logging.warning("illegal packages entry '%s'", name)
                    continue
                if '/' in name or '*' in name:  # for now
                    logging.warning("packages entry with '/' or '*' not implemented yet")
                    continue
                packages.append(name)
        if manifest_yml.get('subdirectories'):
            for newsubdir in manifest_yml['subdirectories']:
                if manifest_yml.get('skip_missing_subdirectories') == "true":
                    if not os.path.exists(directory + "/" + newsubdir):
                        continue
                if newsubdir:
                    subdirectories.append(newsubdir)
        return packages, subdirectories

    def read_project_subdirs(self, filename):
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