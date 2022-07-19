.. _casefoam_cli:

CLI: casefoam
=============


The casefoam cli tools create and run parameter studies

    run casefoam --help for help

    autocompletion can be installed with --install-completion

    casefoam [Tab][Tab]:

.. sourcecode:: bash

    create run


subcommand: create
------------------

the subcommand casefoam create lets you create a template in the given case or run the parameter study from a json already present in the

subsubcommand: from-json
~~~~~~~~~~~~~~~~~~~~~~~~

``casefoam create from-json``:


create the parameter from ``para_study.json``

subsubcommand: template
~~~~~~~~~~~~~~~~~~~~~~~

``casefoam create template``:


create a genCases.py in the current folder that forms the basis of a new parameter study


subcommand: run
---------------

Lets you run all OpenFOAM cases in a folder

subsubcommand: folder
~~~~~~~~~~~~~~~~~~~~~

``casefoam run folder [Folder]``:


Lets you run all OpenFOAM cases in a folder

with ``--nProcs``:

    multiple processes run be run simultaneously

