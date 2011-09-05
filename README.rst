sawfish-build
=============

Build the Debian packages for the great sawfish window manager and rep.

Introduction
------------

The Sawfish window manager is the only window manager for me.
Unfortunately its packages from Debian or Ubuntu tend to be out of
date.  But, it comes with a ``debian/`` build directory so I build my
own.  This package helps build sawfish and its librep and rep-gtk
dependencies.

Howto
-----

This "package" is centered around a `Fabric file
<http://fabfile.org>`_ 
and some patches.
To use it do:

#. Go to some clean work area

#. Copy the patches (keep their names unchanged) and ``fabfile.py``

#. Run "``fab dependencies``" to do one-time installation of some needed packages.

#. Run "``fab build_latest``" to build and install "``librep``", "``rep-gtk``" and "``sawfish``" packages.


This last step is rather monolithic and may fail as it tries to guess
the latest available tagged versions of the three projects and assumes
they go together.  See what finer-grained things are available with
"``fab -l``"

Any applied patches are commited to the local git repo as
"``dpkg-buildpackage``" requires the repo to be clean.

Optional: "``fab xephyr_test``" to test sawfish in the nested Xephyr
xserver.
