
Native OBS SCM bridge helper
============================

Native OBS scm support for the build recipies and additional files. This is bridging an external authorative
scm repository into OBS. Any source change or merge workflow must be provided via the scm repository 
hoster in this scenario.

Only git is supported atm, but this can be extended later to further systems.

It is not recommended to put large binary files into git directly as this won't scale. Use the
asset support instead, which is described in pbuild documentation:

  http://opensuse.github.io/obs-build/pbuild.html#_remote_assets

These assets will be downloaded by osc and OBS. The verification via sha256 sum is optional.

HOWTO manage a single package
=============================

The current way to define a git repository for an OBS package is using the `scmsync`
element inside the package meta.

```
<scmsync>https://github.com/foo/bar</scmsync>
```

For doing a local checkout use the currently experimental osc from

  https://download.opensuse.org/repositories/home:/adrianSuSE:/OBSGIT/

This version allows you to do

# osc co $project <$package>

which will create a git repository inside of the classic osc checkout.

The only further tested functionality is to do local builds atm.

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

 * lfs=1 CGI parameter to include LFS resources

 * arch=<ARCH> CGI parameter to specify arch specific assets downloads

 * keepmeta=1 CGI parameter to include full git vcs data (.git directory)

 * subdir=<DIRECTORY> CGI parameter to package only a subdirectory

TODO
====

 * signature validation

 * find a better way to store files in .osc and .assets of the checkout, as
   they do not belong to the git repository
    auto extending .gitignore? (esp. when downloading asset files?)

 * make cpio generation bit identical (avoiding mtime from clone)

