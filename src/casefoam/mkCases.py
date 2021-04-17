from casefoam import CaseFoamStructure
from casefoam.utility import mkRmCases, mkAllRunClean
import shutil


def mkCases(baseCase, caseStructure, caseData, hierarchy, writeDir=None):
    r"""Make OpenFOAM cases.

    Make OpenFOAM cases based on a base case. The structure and folder
    hierarchy can be choosen freely. The case structure is set with an list of
    items to be changed. For example::

        [[parent1, parent2],
         [child1, child2, child3],
         [grandchild1, grandchild2]]

    gives cases::

        parent1/child1/grandchild1
        ...
        parent2/child3/grandchild2

    Parameters
    ----------
    baseCase : str
        Directory of the base case. This directory contains all cases and
        the baseCase directory. Do not use 'baseCase' baseCase directory
        since this is the baseCaseDir. For example:

        >>> baseCase = '/compressible/rhoCentralFoam/forwardStep/'

    caseStructure : list
        List of parent, child and grandchild names.
    caseData : dict
        Dictionary of data to update. For each parent, child, grandchild ...
        name, a set of data is given to update.
        The structure of the caseDir dictionary looks like the following:

        >>> {'parent1': {'path/to/paramter': {content_to_change}},
             ...
             'grandchild2': {'path/to/paramter': {content_to_change}}}

         To manipulate a text file that is not in the OpenFOAM dictionary
         format you can pass ``'#!stringManipulation'`` as
         ``{content_to_change}``.
         This will replace a `STRINGMARKER` with a `string` in the given file.

         >>> {'replace a string': {
                 'path/to/textFile': {
                     '#!stringManipulation': {'STRINGMARKER', 'string'}}}}

         Further a bash command can be executed for a specific case, by
         replacing the ``'path/to/parameter'`` with ``'#!bash'`` and passing
         the command as value. If the word ``'#!destination'`` occurs in the
         passed value, ``'#!destination'`` will be replaced by the respective
         case directory.

         >>> # print a message to the console
         >>> {'#!bash': 'echo "Here could be your command"'}
         >>> # copy a mesh from a directory into the respective case
         >>> {'#!bash': 'cp -rn meshes/coarse/constant #!destination'}
    hierarchy : {'flat', 'tree'}
        Hierarchy in which the case directory will be created.

        * 'flat': Creates the structure `parent_child_grandchild`.
        * 'tree': Creates the structure `parent/child/grandchild`.
    writeDir : str
        Copy the base case to this directory and generate cases inside
        of it. Default is ``None``.

    Returns
    -------
        Generates a baseCase directory inside the base case and the OpenFOAM
        cases in a desired directory hierarchy with updated parameter files.
        In addition a bash script `rmCases` is generated to bring the case
        folder back to it's original structure and a Allrun and Allclean
        script is generated.

    Examples
    --------
    To get the correct structure of the dictionary for the input
    ``{content_to_change}`` in ``caseData`` you can use PyFoam.

    >>> import PyFoam.RunDictionary.ParsedParameterFile as PPF
    >>> U = PPF.ParsedParameterFile('forwardStep/0/U')
    >>> U.content
    {'boundaryField': {'bottom': {'type': 'symmetryPlane'},
      'defaultFaces': {'type': 'empty'},
      'inlet': {'type': 'fixedValue', 'value': 'uniform (3 0 0)'},
      'obstacle': {'type': 'slip'},
      'outlet': {'inletValue': 'uniform (3 0 0)',
       'type': 'inletOutlet',
       'value': 'uniform (3 0 0)'},
      'top': {'type': 'symmetryPlane'}},
     'dimensions': '[ 0 1 -1 0 0 0 0 ]',
     'internalField': 'uniform (3 0 0)'}

    """
    try:
        if writeDir:
            try:
                shutil.copytree(baseCase, writeDir)
            except FileExistsError:
                pass

            CaseFoamStructure(writeDir, caseStructure, caseData, hierarchy)
        else:
            CaseFoamStructure(baseCase, caseStructure, caseData, hierarchy)
    except KeyboardInterrupt:
        pass

    if writeDir:
        mkRmCases(writeDir, caseStructure, isWriteDir=True)
        mkAllRunClean(writeDir)
    else:
        mkRmCases(baseCase, caseStructure)
        mkAllRunClean(baseCase)
