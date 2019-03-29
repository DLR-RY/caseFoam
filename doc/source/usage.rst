.. _usage:

Usage
=====

CaseFOAM allows the creation and analysis of parameter-studies for OpenFOAM cases.


Generation of Parameter studies
-------------------------------

To setup two cases with a different ``'internalField'`` , we have to
define the structure of the cases. This has to be a ``list`` within a ``list``.

.. sourcecode:: python

    >>> caseStructure = [['Ux1', 'Ux2']]

CaseFOAM's ``mkCases`` method generates the caseStructure which is defined above.

.. sourcecode:: python

    >>> import casefoam
    >>> baseCase = 'pitzDaily'
    >>> casefoam.mkCases(baseCase, caseStructure, caseData, hierarchy='tree')

There are two options available how the cases are created specified by the function
parameter``hierarchy`` which can be ``flat`` (pitzDaily_Ux1, pitzDaily_Ux1)
or ``tree`` (pitzDaily/Ux1, pitzDaily/Ux2). The variable baseCase is the path to
the case we want to modify.

``caseData`` specifies the data for the case manipulation. It links the entries from
the ``caseStructure`` to the modification dictionaries.

.. sourcecode:: python

    >>> caseData = {'Ux1': update_Ux1, 'Ux2': update_Ux2}

The values for ``'Ux1'`` and ``'Ux2'`` should modify e.g the internal
velocity field of the case

.. sourcecode:: python

    >>> update_Ux1 = {'0/U': {'internalField': 'uniform (1 0 0)'}}
    >>> update_Ux2 = {'0/U': {'internalField': 'uniform (2 0 0)'}}


There a three different options how the modification data can be specified

    - replacing a string inside the specified files
    - executing a bash script
    - specifying a dictionary

But all method have in common that the are dictionaries.

replacing strings
~~~~~~~~~~~~~~~~~

Manipulating a file by exchanging a string is straighforward, just specify the file in which the string should be replaced
After the filename a dictionary follows starting with the keyword ``#!stringManipulation`` with another
dictionary with the string and the replacement values.


.. sourcecode:: python

    update_grid1 = {
        'system/blockMeshDict': {'#!stringManipulation': {'varA': '23',
                                                          'varB': '8',
                                                          'varC': '19',
                                                          'varD': '42',
                                                          'varE': '4'}}
    }


In this case we would replace the varA to varE in the ``system/blockMeshDict``


executing a script
~~~~~~~~~~~~~~~~~~

To execute bash commands from casefoam create a dictionary with the keyword ``#!bash`` followed by a command

.. sourcecode:: python

    update_coarse = {
        'Allrun.slurm': {'#!stringManipulation': {'JOBNAME': 'coarse'}},
        '#!bash': 'cp -rn meshes/coarse/constant koala/coarse'}


Here, we replace the string JOBNAME in the Allrun.slurm script and copy the mesh
from a different location in our case

specifying a dictionary
~~~~~~~~~~~~~~~~~~~~~~~

Another variant for changing OpenFOAM files is with the help of the PyFoam.
PyFoam can load openfoam files and represented them as python-dictionaries.
To get the correct format you can use the ``getFileStructure`` utility from
``casefoam.utility``.

.. sourcecode:: python

    >>> import casefoam
    >>> casefoam.utility.getFileStructure('forwardStep/0/U')
    {'boundaryField': {'bottom': {'type': 'symmetryPlane'},
                       'defaultFaces': {'type': 'empty'},
                       'inlet': {'type': 'fixedValue',
                                 'value': 'uniform (3 0 0)'},
                       'obstacle': {'type': 'slip'},
                       'outlet': {'type': 'inletOutlet',
                                  'inletValue': 'uniform (3 0 0)',
                                  'value': 'uniform (3 0 0)'},
                       'top': {'type': 'symmetryPlane'}},
     'dimensions': '[ 0 1 -1 0 0 0 0 ]',
     'internalField': 'uniform (3 0 0)'}

Again, first the filename followed by a dictionary is specified. For every
sub-dictionary in OpenFOAM, a new dictionary needs to be specified. Following
command would  manipulate the inlet velocity:


.. sourcecode:: python

    update_Ux = {
        '0/U': {'boundaryField': {'inlet': {'value': 'uniform (3 0 0)'}}}
    }

.. _casefoam_help:

Help in Python
--------------

If you are running IPython, you can get direct help for the modules.

.. sourcecode:: python

    >>> import casefoam
    >>> help(casefoam.mkCases)
    Make OpenFOAM cases.

    Make OpenFOAM cases based on a base case. The structure and folder
    hierarchy can be choosen freely. The case structure is set with an list of
    items to be changed. For example:

        >>> [[parent1, parent2],
             [child1, child2, child3],
             [grandchild1, grandchild2]]

    gives cases `parent1/child1/grandchild1` ... `parent2/child3/grandchild2`.

.. _post-processing:

Post-Processing
---------------

All post-processing functions return a pandas_ dataframe in the long-format_.
The advantage of this format is that non Nan values are necessary which
frequently happens if multiple cases with different time step size are
compared. The conversion between long and wide format is straighforward and is
achieved with the pandas command pd.pivot_table_.

.. sourcecode:: python

    >>> pd.pivot_table(df,index=df.index, columns=['col_1','col_2'])

Various tools for visualiation of pandas dataframe exist. They have an in-built
function ``plot()`` which generates a matplotlib figure. It plots every column
and is helpful if the dataFrame is in the wide format. Another powerful visualiation
tool is  holoview_ which has his strength in interactive visualiation and combination
with jupyter-notebook. The created figures are interactive and can be
stored in a html which can passed to colleagues.


.. _pandas: http://pandas.pydata.org/pandas-docs/stable/
.. _long-format: https://en.wikipedia.org/wiki/Wide_and_narrow_data
.. _holoview: http://holoviews.org/
.. _pd.pivot_table: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.pivot_table.html


A more examples can be find in the example folder. Here is a basic one:

.. sourcecode:: python

    >>> import casefoam

    >>> # directory of the base case
    >>> baseCase = 'damBreak'

    >>> # list of parent, child and grandchild names
    >>> caseStructure = [['grid1', 'grid2', 'grid3']]

    >>> # probe location
    >>> probeDir = 'probes/0'

    >>> # load probe data
    >>> p = casefoam.time_series(probeDir, 'p', caseStructure, baseCase)

Three functions are available for the post-processing:

    - time_series
    - positional_field
    - posField_to_timeSeries

``time_series`` is intended for plotting time series as probe data or forces.
``positional_field`` can plot fields suchs as sets and surface.
``posField_to_timeSeries`` converts a positional_field to a time series by
reducing the postional field to a single value with a user specified function.

The below video shows the damBreak test case

.. raw:: html

    <video controls src="_static/damBreakVideo.mp4" width="620" height="620" type="video/mp4"></video>

The column height and resolution of the grid is varied with casefoam.
The freesurface at 0.3 seconds can be rendered in a html file with:

.. sourcecode:: python

    import casefoam
    import matplotlib.pyplot as plt
    import pandas as pd
    import holoviews as hv
    hv.extension('bokeh')

    caseStructure = [['height_02', 'height_03', 'height_04'],
                     ['grid1', 'grid2', 'grid3']]
    baseCase = 'Cases'
    surfaceDir = 'freeSurface'
    surface = casefoam.positional_field(solutionDir=surfaceDir,
                                        file='U_freeSurface.raw',
                                        time=0.3,
                                        caseStructure=caseStructure,
                                        baseCase=baseCase)
    surface.columns = ['x','y','z','Ux','Uy','Uz','col_height','res']
    surface_ds = hv.Dataset(surface, [ 'col_height','res'],
                            ['x','y','z','Ux','Uy','Uz'])

holoviews is optimized for the use for the jupyter notebooks. The %%opts arguments
are used to modify the layout of the plot. holoviews renders an interactive plot
which can be exported as html:

.. sourcecode:: python

    %%output filename="contour" fig="html"
    %%opts Scatter [width=600,
                    height=600,
                    title='freeSurface at 0.3s',
                    tools=['hover']]
    %%opts (muted_alpha=0.0)
    surface_ds.to(hv.Scatter,'x','y').overlay('res')


.. raw:: html

    <iframe src="_static/damBreak_surface_03.html" marginwidth="0" marginheight="0" scrolling="no" style="width:960px; height:600px; border:0; overflow:hidden;">
    </iframe>
