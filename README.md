
Native OBS SCM bridge helper
============================

Native OBS scm support for the build recipies and additional files. This is bridging an external authoritative
scm repository into OBS. Any source change or merge workflow must be provided via the scm repository
hoster in this scenario.

Only git is supported atm, but this can be extended later to further systems.

It is not recommended to put large binary files into git directly as this won't scale. Use the
asset support instead, which is described in pbuild documentation:

  http://opensuse.github.io/obs-build/pbuild.html#_remote_assets

These assets will be downloaded by osc and OBS. The verification via sha256 sum is optional.

Alternatively, put large binary files into
[git-lfs](https://git-lfs.github.com/). This service will automatically download
git-lfs assets.

HOWTO manage a single package
=============================

The current way to define a git repository for an OBS package is using the `scmsync`
element inside the package meta.

```
<scmsync>https://github.com/foo/bar</scmsync>
```

For doing a local checkout use a 1.0 release candidate of osc. This version allows
you to do

$ osc co $project [$package]

which will create a git repository inside of the classic osc checkout.

It also supports local building, but you need to use git for any source
modification or operation.

HOWTO manage an entire project
==============================

A git repository can also get defined for entire project. This can be done
via the scmsync element in project meta.

Any top level subdirectory will be handled as package container.

It is recomended to use git submodules for each package if it is a larger
project. This allows partial cloning of the specific package.

Special directives
==================

Special directives can be given via cgi parameters to the bridge. Extend
your url with

 * lfs=0 to skip downloading LFS assets

 * arch=ARCH specify arch for assets downloads (can be used multiple times)

 * keepmeta=1 include full git vcs data (.git directory)

 * subdir=DIRECTORY package only a subdirectory

 * noobsinfo=1 do not write a `_scmsync.obsinfo` file

 * trackingbranch=BRANCH may be used to clone the branch instead of a revision.
                         information is taken from .gitmodules if available.

 * buildtype=TYPE may be used to limit asset types, the default is to download all.
                  Possible values are spec, dsc, fedpkg or golang.
                  (Parameter can be used multiple times)

Special directives for entire projects
======================================

 * projectmode=1 is switching project mode on. The bridge will just prepare
                 package meta files for each subdirectory.

 * onlybuild=DIRECTORY   can be used to specify to only export defined packages
                         without modifing the git source. The parameter can be
                         used multiple times to collect multiple.

Special configuration files
===========================

These configuration files are optional and usually only used on OBS server side.

/etc/obs/services/scm-bridge/critical-instances
  Each line contain a list of critical git server instances. These instances
  are support to be reachable always. In case of errors the OBS server
  will retry always to re-run the server.
  Please note that dropped or not accessible repositories still count as
  an error.

/etc/obs/services/scm-bridge/credentials
  Each line must contain a triplet with a space seperated:

  PROJECT\_NAMESPACE HOSTNAME USERNAME TOKEN/PASSWORD

  These credentials will be used for git cloning when no other credentials
  are defined in the specified URL.

  PROJECT\_NAMESPACE is also valid for all sub projects. When using '*' it is
  valid for all projects.


TODO
====

 * signature validation

 * find a better way to store files in .osc and .assets of the checkout, as
   they do not belong to the git repository
    auto extending .gitignore? (esp. when downloading asset files?)

 * make cpio generation bit identical (avoiding mtime from clone)

