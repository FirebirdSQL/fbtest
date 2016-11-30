============
Introduction
============

Requirements
============

- Python_ version 2.7. If you have Python 3.x already installed, you may try it as FBTest should work
  with it, but it was not tested with Python 3 yet. 

  - `Linux:` If you don't have Python already installed you can get it from your distribution's repository.
  - `Windows & MacOS:` You may download Python installation package from `python.org <http://www.python.org/download/>`_, or from ActiveState_ (recommended).
- Distribute_ module.
- PIP_ installer. It's not strictly necessary, but it makes you life with Python much easier. 
- FDB_ Firebird driver for Python.
- PySVN_ module (optional but recommended).

.. tip:: 

   On Linux you may find Subversion, PySVN, PIP, Distribute and FDB in your distribution repositories.

  

Installation
============


1. Install the `Python` programming language.
2. Install `Distribute`. On Windows and MacOS (or Linux if its not in your repository) download
   `distribute_setup.py`_ and run next command::

      python distribute_setup.py

   You can find detailed installation instructions for Distribute  
   `here <https://pypi.python.org/pypi/distribute#installation-instructions>`_.

3. Install `pip`. On Windows and MacOS (or Linux if its not in your repository) download
   `get-pip.py`_ and run next command::

      python get-pip.py

   You can find detailed installation instructions for PIP 
   `here <http://www.pip-installer.org/en/latest/installing.html>`_.
4. Install `FDB`. If you have installed `PIP`, you can simply run next command::

      pip install fdb

   to install FDB from PyPI (Python Package Index). Otherwise you have to download FDB, unpack it and run::

      python setup.py install

   from directory where you unpacked it.
5. Install `PySVN` module.

   On Linux you should find it in your distribution repository (as `python-svn` or `pysvn`). On Windows and MacOS you need to download and install appropriate installation kit for PySVN_.

   Although fbtest uses Subversion to access Firebird project's repository, you shouldn't need to install it, as it's part of pysvn installation kit for Windows/MacOS and should be installed automatically on Linux (as dependency to pysvn).
6. Install `fbtest`. 

   a) If you want to run Firebird test suite, but do not develop new tests, use next method.

      If you have installed `PIP`, you can simply run next command::

         pip install fbtest

      to install it from PyPI. Otherwise you have to download it from Firebird website, unpack it and run::

         python setup.py install

   b) If you want to run tests and also create new ones (or develop fbtest itself), make a checkout of `this path <http://svn.code.sf.net/p/firebird/code/qa/fbtest/trunk/>`_ from Firebird Subversion repository, and then run::

         python setup.py develop

      You should also download fbtedit - GUI Test editor for Windows.

Test Repository Initialization
==============================

Create directory where you want it stored and run next command::

   fbt_update repository

It will fetch tests and all other necessary files directly from Firebird project subversion repository.

.. important::

   If you don't have PySVN_ module installed, you have to checkout :ref:`test-repository` manually.


.. _Python: http://www.python.org
.. _ActiveState: http://www.activestate.com/activepython/downloads
.. _FDB: http://pypi.python.org/pypi/fdb
.. _PIP: http://pypi.python.org/pypi/pip
.. _Distribute: https://pypi.python.org/pypi/distribute
.. _Subversion: http://subversion.tigris.org/
.. _PySVN: http://pysvn.tigris.org/project_downloads.html
.. _distribute_setup.py: http://python-distribute.org/distribute_setup.py
.. _get-pip.py: https://raw.github.com/pypa/pip/master/contrib/get-pip.py
.. _PyPI: https://pypi.python.org/

