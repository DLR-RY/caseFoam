import os
import pandas as pd


def getCases(solutionDir, caseStructure, baseCase, postDir='postProcessing'):
    """Get cases.

    Get cases out of the ``caseStructure`` that contain a solution directory.

    Parameters
    ----------
    solutionDir : str
        Solution directory in the OpenFOAM case ``postProcessing`` directory.
    caseStructure : list
        List of parent, child and grandchild names.
    baseCase : str
        Root directory of all cases.

    Returns
    -------
    cases : list
        List with relative path to all cases containg a ``surfaces`` directory.
    caseCombs : list
        A list with all case combinations as tuples.

    """
    if(caseStructure is None):
        return [os.path.join(baseCase, postDir, solutionDir)], [(baseCase,)]

    multiIndex = pd.MultiIndex.from_product(caseStructure)
    allCaseCombs = multiIndex.values
    cases = list()
    caseCombs = list()

    try:

        for caseComb in allCaseCombs:
            _len = len(caseComb)
            _path = baseCase

            for i in range(_len):
                _path = os.path.join(_path, caseComb[i])

            _path = os.path.join(_path, postDir, solutionDir)

            if os.path.isdir(_path):
                cases.append(_path)
                caseCombs.append(caseComb)
    except AttributeError:  # handle caseStructures with only one level

        for caseComb in allCaseCombs:
            _path = os.path.join(baseCase, caseComb, postDir, solutionDir)

            if os.path.isdir(_path):
                cases.append(_path)
                caseCombs.append((caseComb,))  # write as tuple

    return cases.copy(), caseCombs.copy()


def __get_timeSeries(solutionFile, columnNames=None):
    """Load timeSeries data.

    Load a timeSeries

    Parameters
    ----------
    solutionFile : str
        Path to the solution file.
    columnNames : list, optional
        List of forces.

    Returns
    -------
    pandas.DataFrame
        If a list of columnNames is given, the output will have the
        ``columnNames`` as columns. If no columnNames are given the
        columns will be ``[1, 2, ..., n]``.

    """
    _outputDf = pd.read_csv(solutionFile, comment='#',
                            sep='[() \t]+', engine='python', header=None)
    # drop last column as it terminates with
    if(pd.isnull(_outputDf.iloc[0, -1])):
        _outputDf.drop(_outputDf.columns[[-1, ]], axis=1, inplace=True)

    _outputDf.set_index(0, inplace=True)
    if(columnNames is not None):
        _outputDf.columns = columnNames

    return _outputDf


def __get_posField(solutionFile):
    """Load pos data.

    Load a posSeries

    Parameters
    ----------
    solutionFile : str
        Path to the solution file

    Returns
    -------
    pandas.DataFrame

    """

    try:
        suffix = os.path.splitext(solutionFile)[1]
        if suffix in ('.xy', '.raw'):
            return pd.read_csv(solutionFile, comment='#',
                               delim_whitespace=True, header=None)
        elif suffix == '.csv':
            return pd.read_csv(solutionFile)
        else:
            raise Exception(
                'File Format : ', suffix, ' is not supported only xy ',
                'raw csv. Please change the setFormat or',
                'surfaceFormat in the ``controlDict`` to ``csv`` or ``raw``'
            )
    except FileNotFoundError:
        return None


def time_series(solutionDir, file, caseStructure=None, baseCase='.',
                columnNames=None):
    """Load timeSeries(e.g probes, forces etc)

    Loads a timeseries of a given case and save them into one pandas.DataFrame.
    multiple cases can be combined with the caseStructure argument

    Parameters
    ----------
    solutionDir : str
        Solution directory in the OpenFOAM case ``postProcessing`` directory.
    file : str
        File name of the solution file.
    caseStructure : list, optional
        List of parent, child and grandchild names::

            [[parent1, parent2],
             [child1, child2, child3],
             [grandchild1, grandchild2]]
    baseCase : str, optional
        Root directory of all cases.
    columnNames : list, optional
        List of columnNames.

    Returns
    -------
    outputDf : pandas.DataFrame
        pandas.DataFrame with solutions for all times.

    """
    outputDf = pd.DataFrame()
    cases, caseCombs = getCases(solutionDir, caseStructure, baseCase)

    for i, caseComb in enumerate(caseCombs):
        currentSolutionFile = os.path.join(cases[i], file)
        if os.path.exists(currentSolutionFile):
            try:
                currentDataFrame = __get_timeSeries(currentSolutionFile,
                                                    columnNames)
            except pd.errors.EmptyDataError:
                print('Note: {} was empty. Skipping.'.format(currentSolutionFile))
                continue


            counter = 0
            for variables in caseComb:
                currentDataFrame['var_' + str(counter)] = variables
                counter += 1

            currentDataFrame.index.name = 't'
            outputDf = pd.concat([outputDf,currentDataFrame], axis=0, join='outer')
            del currentDataFrame

    return outputDf


def positional_field(solutionDir, file, time, caseStructure=None, baseCase='.'):
    """Load positionalField(surfaces and sets).

    Loads a positionalField of a given case and save them into one
    pandas.DataFrame. multiple cases can be combined with the caseStructure
    argument

    Parameters
    ----------
    solutionDir : str
        Solution directory in the OpenFOAM case ``postProcessing`` directory.
    file : str
        File name of the solution file.
    time : float
        Point of time at which to load the field.
    caseStructure : list, optional
        List of parent, child and grandchild names::

            [[parent1, parent2],
             [child1, child2, child3],
             [grandchild1, grandchild2]]
    baseCase : str, optional
        Root directory of all cases.

    Returns
    -------
    outputDf : pandas.DataFrame
        pandas.DataFrame with solutions for all times.

    """
    outputDf = pd.DataFrame()
    cases, caseCombs = getCases(solutionDir, caseStructure, baseCase)

    for i, caseComb in enumerate(caseCombs):
        currentSolutionFile = os.path.join(cases[i], str(time), file)
        if os.path.exists(currentSolutionFile):
            try:
                currentDataFrame = __get_posField(currentSolutionFile)
            except pd.errors.EmptyDataError:
                print('Note: {} was empty. Skipping.'.format(currentSolutionFile))
                continue
            counter = 0
            for variables in caseComb:
                currentDataFrame['var_' + str(counter)] = variables
                counter += 1

            outputDf = pd.concat([outputDf,currentDataFrame], axis=0, join='outer')
            del currentDataFrame

    return outputDf


def posField_to_timeSeries(solutionDir, file, postFunction, caseStructure=None,
                           baseCase='.', **kwargs):
    """Converts multiple posionalFields to timeSeries with a function

    Load all postional Fields of a given case, manipulate the data for each
    time step and save the manipulated results into one pandas.DataFrame for
    all times.

    Parameters
    ----------
    solutionDir : str
        Solution directory in the OpenFOAM case ``postProcessing`` directory.
    file : str
        File name of the solution file.
    postFunction : function
        User function to manipulate the solution data
        ``['x', 'y', 'z', 'values', ...]``. The function must return
        output DataFrame should has and  has to have the
        parameters ``(caseComb, time, currentDataFrame)``
    caseStructure : list, optional
        List of parent, child and grandchild names::

            [[parent1, parent2],
             [child1, child2, child3],
             [grandchild1, grandchild2]]
    baseCase : str, optional
        Root directory of all cases.
    **kwargs
        Keyword arguments if needed by ``postFunction``.

    Returns
    -------
    outputDf : pandas.DataFrame
        pandas.DataFrame with solutions for all times.

    Examples
    --------
    Define a user ``postFunction``.

    >>> def userFunction(caseComb, time, currentDataFrame):
        t = time
        minimum = currentDataFrame.iloc[:, 1].min()
        mean = currentDataFrame.iloc[:, 1].mean()
        maximum = currentDataFrame.iloc[:, 1].max()
        df = pd.DataFrame(np.array([time, minimum, mean, maximum],
                          ndmin=2),
                          columns=['time', 'min', 'mean', 'max'])
        df = df.set_index('time')
        return df

    """
    outputDf = pd.DataFrame()
    cases, caseCombs = getCases(solutionDir, caseStructure, baseCase)

    for i, caseComb in enumerate(caseCombs):
        times = os.listdir(cases[i])

        for time in times:
            currentSolutionFile = os.path.join(cases[i], time, file)
            try:
                surfaceDataFrame = __get_posField(currentSolutionFile)
            except pd.errors.EmptyDataError:
                print('Note: {} was empty. Skipping.'.format(currentSolutionFile))
                continue
            funcDataFrame = postFunction(
                caseComb, float(time), surfaceDataFrame, **kwargs)

            counter = 0
            for variables in caseComb:
                funcDataFrame['var_' + str(counter)] = variables
                counter += 1
            outputDf = pd.concat([outputDf,funcDataFrame], axis=0, join='outer')
            del surfaceDataFrame

    return outputDf
