#!/usr/bin/python3
# Example application to parse a local git repository using list_packages

import argparse
import logging
import os
import sys

import obs_scm_bridge


def main():
    parser = argparse.ArgumentParser(
        description='Parse a local git repository and list packages'
    )
    parser.add_argument(
        'directory',
        help='Path to the git repository',
        nargs='?',
        default='.'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a directory")
        sys.exit(1)

    if not os.path.isdir(os.path.join(args.directory, '.git')):
        print(f"Warning: '{args.directory}' does not appear to be a git repository")

    packages = obs_scm_bridge.list_packages(args.directory)

    print(f"Found {len(packages)} entries in '{args.directory}':\n")
    print(f"{'Package':<30} {'Subdir':<30} {'Submodule URL'}")
    print("-" * 80)

    for pkg, subdir, submod in packages:
        print(f"{pkg:<30} {subdir:<30} {submod or '-'}")


if __name__ == '__main__':
    main()
