sawfish-build
=============

Build the Debian packages for the great sawfish window manager and rep.

This is housed at github
<https://github.com/brettviren/sawfish-build>

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

#. Copy the patches, if any (keep their names unchanged) and ``fabfile.py``

#. Run "``fab dependencies``" to do one-time installation of some needed packages.

#. Run "``fab build_latest``" to build and install "``librep``", "``rep-gtk``" and "``sawfish``" packages.


This last step is rather monolithic and may fail as it tries to guess
the latest available tagged versions of the three projects and assumes
they go together.  See what finer-grained things are available with
"``fab -l``"

If you do things manually, you must go through the chain of operations
on each package in order of librep, rep-gtk and finally sawfish.  Here
is an example with librep.

::

  fab clone librep
  fab checkout librep:0.92.2
  fab patch librep           # if needed
  fab clean librep
  fab build librep
  fab install librep:0.92.2  # or use dpkg yourself

Any applied patches are commited to the local git repo as
"``dpkg-buildpackage``" requires the repo to be clean.

Optional
--------

Use "``fab xephyr_test``" to test sawfish in the nested Xephyr
xserver.

Potential Problems
------------------

Tags
  Not always are the ``sawfish``, ``rep-gtk`` and ``librep`` releases
  tagged in their git repositories.  You can first clone the projects
  (``fab clone:PROJECT``) enter the directory and run ``gitk``.  This
  is usually enough to find the commit that was used for the release.
  You can then tag it yourself.

``debian/changelog``
  The ``PACKAGE/debian/changelog`` may need updating.  Add a comment
  keeping the same format as the others.

Package signing
  The last step is signing the package.  This will likely fail unless
  the changelog comment uses a name that has a matching GPG key.
