
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

HOWTO
=====

The current temporary way to define a git repository inside of an OBS package is to mis-used the title
element inside of the package meta. Set it to

GIT:<public_git_url>

For doing a local checkout use the currently experimental osc from

  https://download.opensuse.org/repositories/home:/adrianSuSE:/OBSGIT/

This version allows you to do

# osc co $project <$package>

which will create a git repository inside of the classic osc checkout.

The only further tested functionality is to do local builds atm.

TODO
====

 * Clean integration via a proper meta data defintion.

 * Project level support: Packages are defined via a gitlab/github project.

 * osc upstream integration

 * find a better way to store files in .osc and .assets of the checkout, as
   they do not belong to the git repository
    auto extending .gitignore? (esp. when downloading asset files?)

