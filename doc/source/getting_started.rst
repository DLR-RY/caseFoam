Getting started
===============

.. _installing-casefoam:

Installing CaseFOAM
-------------------

In order to use the Python module you need the ``PyFoam`` package.

Run the ``setup.py``.

.. sourcecode:: bash

   $ python setup.py install
   $ pip install pyfoam
  
The installation of pyviz_ is not necessary but we recommended:

.. _pyviz: http://pyviz.org/index.html

.. sourcecode:: bash

   $ conda install -c pyviz/label/dev pyviz


Details regarding the installation of pyviz are avaiable here_.

.. _here: http://pyviz.org/installation.html

User's Guide
------------

For a full documentation change into `doc` and build the documentation for
example as html.

.. sourcecode:: bash

    $ cd doc/
    $ make html
    $ firefox build/html/index.html
