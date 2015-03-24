Contribute
==========

Toolchain
---------

### Prequirements

* blender
* python
* pep8

(within blender modules)

* pylint
* sphinx

#### Path

Substitute `<path/to/modules>` with one of the following:

on Mac OSX

    ~/Library/Application\ Support/Blender/<version>/scripts/modules/

on Windows

    <drive>:\Documents and Settings\<username>\AppData\Roaming\Blender Foundation\Blender\<version>\scripts\modules\

on \*nix:

    ~/.blender/<version>/scripts/modules/

### Documentation

#### Install requirments

    $ pip install --upgrade -t <path/to/modules> sphinx

#### Build

    $ make docs

### Static analysis & compliance

#### Install requirments

    $ pip install --upgrade -t <path/to/modules> pylint

#### Run

    make pep8
    make pylint

### Unittest

    make test
