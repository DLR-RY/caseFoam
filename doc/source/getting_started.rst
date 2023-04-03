.. _getting_started:

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

.. Link is outdated and pyviz ships with default anaconda as far as I understand. To my understanding one could even delete the conda install part.

User's Guide
------------

For a full documentation change into `doc` and build the documentation for
example as html.

.. sourcecode:: bash

    $ cd doc/
    $ make html
    $ firefox build/html/index.html
