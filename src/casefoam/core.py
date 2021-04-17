from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from collections.abc import Mapping
import os
import re
import shutil
import subprocess


def _errorCleanUp(baseCase, cases):
    """Clean up after error.

    Brings baseCase back to original structure when error occurs.

    Parameters
    ----------
    baseCase : string
        Path to the baseCase directory.
    cases : list
        List of parent, child and grandchild names.

    """
    # remove cases
    for case in cases[0]:
        shutil.rmtree(os.path.join(baseCase, case), ignore_errors=True)

    # move `baseCase`/baseCase/ content to `baseCase`/
    try:
        for src in os.listdir(os.path.join(baseCase, 'baseCase')):
            shutil.move(os.path.join(baseCase, 'baseCase', src),
                        os.path.join(baseCase, ''))

        os.rmdir(os.path.join(baseCase, 'baseCase'))
    except FileNotFoundError:
        pass

    exit()


# -----------------------------------------------------------------------------
# class CaseFoamManipulator
# -----------------------------------------------------------------------------
class CaseFoamManipulator(object):
    """OpenFOAM case based on a base case.

    Generates a OpenFOAM case based on a base case and manipulate it.

    Parameters
    ----------
    baseCase : str
        Directory of the base case.

    """

    def __init__(self, baseCase):
        self.baseCase = baseCase
        if os.path.exists(os.path.join(self.baseCase, 'baseCase')):
            self.baseCaseDir = os.path.join(self.baseCase, 'baseCase')

    def loadParameter(self, parameterFile, caseDir='baseCase'):
        """Load a parameter file.

        Load a parameter File and make it a new attribute of the case.

        Parameters
        ----------
        parameterFile : str
            Parameter file.
        caseDir : str
            Directory to the case. If `baseCase` is returned, the baseCase
            directory will be used.

        Attributes
        ----------
        parameter
            Parameter of the loaded parameter file.

        Examples
        --------
        >>> case.loadParameter("0/U")
        >>> case.U

        """
        if 'baseCase' in caseDir:
            try:
                _parameterFilePath = os.path.join(self.baseCaseDir,
                                                  parameterFile)
            except AttributeError:
                _parameterFilePath = os.path.join(self.baseCase,
                                                  parameterFile)
        else:
            _parameterFilePath = os.path.join(caseDir, parameterFile)

        try:
            _parameter = ParsedParameterFile(_parameterFilePath)
        except FileNotFoundError:
            print('ParameterFile not found: No such OpenFOAM parameter file: '
                  '\'%s\'' % parameterFile)
            _errorCleanUp(self.baseCase, self.caseStructure)

        return _parameter

    def updateParameter(self, parameter, parameterUpdate):
        """Update content of a parameter.

        Parameters
        ----------
        parameter : str
            Parameter to update.
        parameterUpdate : dict
            Dictionary with parts to update.

        Attributes
        ----------
        parameter
            Updated parameter

        Examples
        --------
        >>> case.U.content
        {'boundaryField': {'bottom': {'type': 'symmetryPlane'},
          'defaultFaces': {'type': 'empty'},
          'inlet': {'type': 'fixedValue', 'value': 'uniform (2 0 0)'},
          'obstacle': {'type': 'slip'},
          'outlet': {'inletValue': 'uniform (3 0 0)',
           'type': 'inletOutlet',
           'value': 'uniform (3 0 0)'},
          'top': {'type': 'symmetryPlane'}},
         'dimensions': '[ 0 1 -1 0 0 0 0 ]',
         'internalField': 'uniform (3 0 0)'}

        >>> update = {'boundaryField': {
                        'inlet': {'value': 'uniform (1 0 0)'}}}

        >>> case.updateParameter('U', update)

        >>> case.U.content
        {'boundaryField': {'bottom': {'type': 'symmetryPlane'},
          'defaultFaces': {'type': 'empty'},
          'inlet': {'type': 'fixedValue', 'value': 'uniform (1 0 0)'},
          'obstacle': {'type': 'slip'},
          'outlet': {'inletValue': 'uniform (3 0 0)',
           'type': 'inletOutlet',
           'value': 'uniform (3 0 0)'},
          'top': {'type': 'symmetryPlane'}},
         'dimensions': '[ 0 1 -1 0 0 0 0 ]',
         'internalField': 'uniform (3 0 0)'}

        """
        def _innerUpdate(_param, _paramUp):
            for key, value in _paramUp.items():
                if isinstance(value, Mapping):
                    _param[key] = _innerUpdate(_param.get(key, {}), value)
                else:
                    _param[key] = value
            return _param

        parameter.content = _innerUpdate(getattr(parameter, 'content'),
                                         parameterUpdate)

    def updateString(self, caseStringFile, replaceMarker, string):
        """Update string in text file.

        Parameters
        ----------
        caseStringFile : str
            Path to the manipulated text file.
        replaceMarker : str
            String in text which should be replaced.
        string : str
            String to replace `replaceMarker`.

        """
        with open(caseStringFile) as _caseStringFile:
            stringFile = _caseStringFile.read()

        with open(caseStringFile, 'w') as _caseStringFile:
            stringFile = re.sub(replaceMarker, string, stringFile)
            _caseStringFile.write(stringFile)


# -----------------------------------------------------------------------------
# class CaseFoamStructure
# -----------------------------------------------------------------------------
class CaseFoamStructure(CaseFoamManipulator, ParsedParameterFile):
    """

    Parameters
    ----------
    baseCase : str
        Directory of the base case.
    caseStructure : list
        List of parent, child and grandchild names.
    caseData : dict
        Dictionary of data to update.
    hierarchy : {'flat', 'tree'}
        Hierarchy in which the case directory will be created.

    """

    def __init__(self, baseCase, caseStructure, caseData, hierarchy):
        self.baseCase = baseCase
        self.caseStructure = caseStructure
        self.caseData = caseData
        self.hierarchy = hierarchy
        self._tmpTree = list()
        self._tree = list()
        self._baseCaseDir()
        self._recursiveIteration(caseStructure, level=0)

    def _baseCaseDir(self):
        """Generate baseCaseDir.

        Generates the `baseCase` directory inside the as ``baseCase`` defined
        directory and move all the content to the `baseCase` directory.

        """
        self.baseCaseDir = os.path.join(self.baseCase, 'baseCase')
        try:
            baseFolder = os.listdir(self.baseCase)
        except FileNotFoundError:
            print('baseCase not found: No such file or directory: '
                  '\'%s\'' % self.baseCaseDir)
            _errorCleanUp(self.baseCase, self.caseStructure)

        try:
            os.mkdir(self.baseCaseDir)
            for folder in baseFolder:
                shutil.move(os.path.join(self.baseCase, folder),
                            self.baseCaseDir)
        except OSError:
            return None

    def _recursiveIteration(self, caseStructure, level):
        """Recursive iteration.

        Iterate through the caseStructure list to get a case list.

        Parameters
        ----------
        caseStructure : list
            List of parent, child and grandchild names.
        level : int
            Level in the hierarchy of the caseStructure.

        Attributes
        ----------
        case : list
            List of parent, child and grandchild name of a single case.

        """
        try:
            # append subCase to _tmpTree until running out of index of the
            # caseStructure
            for subCase in self.caseStructure[level]:
                self._tmpTree.append(subCase)
                self._recursiveIteration(subCase, level + 1)
        except IndexError:
            # change to the next case by going from grandchild1 to child1 and
            # from child1 to grandchild2. If all cases for the grandchildren
            # are and child1 are generated, change to child2 and continue this
            # loop from bottom to top.
            try:
                # change _tree to have all parents, children, grandchild, ...
                # in one list e.g. if _tmpTree=['T2', 'p1'] and
                # _tree=['Ux1', 'T1', 'p2'], _tree will be changed to
                # ['Ux1', 'T2', 'p1'].
                self._tree.reverse()

                for _level, _subCase in enumerate(reversed(self._tmpTree)):
                    self._tree[_level] = _subCase

                self._tree.reverse()
            except IndexError:
                self._tree = self._tmpTree
                self.case = self._tree

            self._tmpTree = list()
            level -= 1
            self._main()

    def makeStructure(self, hierarchy, case, seperator='_'):
        """Make structure.

        Makes case directory in prefered structure.

        Parameters
        ----------
        hierarchy : {'flat', 'tree'}
            Hierarchy in which the case directory will be created.
        case : list
            List of parent, child, grandchild, ... of a case.
        seperator : str
            Seperator for flat folder hierarchy.

        """
        if hierarchy is 'flat':
            relCaseDir = seperator.join(case)
            self.caseDir = os.path.join(self.baseCase, relCaseDir)
        elif hierarchy is 'tree':
            relCaseDir = os.sep.join(case)
            self.caseDir = os.path.join(self.baseCase, relCaseDir)
        else:
            print('Hierarchy error: No such hierarchy option known: %s\n'
                  '\n'
                  'Valid arguments for hierarchy are \'tree\' or \'flat\''
                  % hierarchy)
            _errorCleanUp(self.baseCase, self.caseStructure)

        try:
            shutil.copytree(self.baseCaseDir, self.caseDir)
        except OSError:
            shutil.rmtree(self.caseDir)
            shutil.copytree(self.baseCaseDir, self.caseDir)

    def _main(self):
        """Generates a single case."""
        self.makeStructure(self.hierarchy, self.case)

        for item in self.case:
            # manipulate all OpenFOAM files defined by caseData step by step
            # e.g. first change parent1 then child1 and so on

            # check if condtitions for the caseData are given and set the
            # caseDataItem dict
            try:
                if list(self.caseData[item]) in self.caseStructure:
                    for caseCondition in list(self.caseData[item]):
                        if caseCondition in self.case:
                            caseDataItem = self.caseData[item][caseCondition]
                else:
                    caseDataItem = self.caseData[item]
            except KeyError:
                print(
                    'Case not found: No case %s found as key in the caseData'
                    ' dict\n'
                    '\n'
                    'Following caseData keys are given:\n'
                    '%s' % (item, list(self.caseData.keys()))
                )
                _errorCleanUp(self.baseCase, self.caseStructure)

            for key, value in caseDataItem.items():
                parameterFilePath = os.path.join(self.caseDir, key)

                # execute bash command
                # NOTE: '#!bash' needs to be checked first. If it is checked
                #       after '#!stringManipulation' an error is raised because
                #       'value' has then no keys.
                if key == '#!bash':
                    if '#!destination' in value:
                        value = value.replace('#!destination', self.caseDir)
                    subprocess.call(value, shell=True)
                # manipulate a string in file if #!stringManipulation is a key
                elif '#!stringManipulation' in value.keys():
                    stringParameters = value['#!stringManipulation'].items()

                    # convert dict_items to list
                    for stringParameter in list(stringParameters):
                        replaceMarker, string = stringParameter
                        self.updateString(parameterFilePath, replaceMarker,
                                          string)
                else:
                    parameter = self.loadParameter(key, self.caseDir)
                    self.updateParameter(parameter, value)
                    parameter.writeFile()
