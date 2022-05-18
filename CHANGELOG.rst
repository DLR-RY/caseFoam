version 0.0.1
=============

0.0.1 (2021-04-14)
------------------

* First release on PyPI.


version 0.0.2
=============

0.0.2 (2021-04-14)
------------------

* First release on PyPI.


version 0.0.3
=============

0.0.3 (2021-04-14)
------------------

* First release on PyPI.


version 0.0.4
=============

0.0.4 (2021-04-14)
------------------

* First release on PyPI.

version 0.1.0
=============

0.1.0 (2022-02-16)
------------------

* added CI
* replaced append with concat

version 0.1.1
=============

0.1.1 (2022-05-18)
------------------

* new Function: of_cases finds all OpenFOAM cases in folder

version 0.2.0
=============

0.2.0 (2022-05-18)
------------------

* new Function: profiling allows to load profiling data from OpenFOAM

.. sourcecode:: cpp

    add profiling to system controlDict:
    profiling
    {
        active      true;
        cpuInfo     false;
        memInfo     false;
        sysInfo     false;
    }

.. sourcecode:: python

    prof = casefoam.profiling(time=0,processorDir="", caseStructure=caseStructure,baseCase=baseCase)
