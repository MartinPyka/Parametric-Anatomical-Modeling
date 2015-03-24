Contribute
==========

Check compliance
----------------

    make pep8

Build documentation
-------------------

Substitute `<path/to/modules>` with one of the following:

on Mac OSX

    ~/Library/Application\ Support/Blender/<version>/scripts/modules/

on Windows

    <drive>:\Documents and Settings\<username>\AppData\Roaming\Blender Foundation\Blender\<version>\scripts\modules\

on \*nix:

    ~/.blender/<version>/scripts/modules/

Installing sphinx:

    $ pip install --upgrade -t <path/to/modules> sphinx

Building documentation:

    $ make docs

Run testsuite
-------------

    make test
