import os
from typing import List
import pandas as pd
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile


def getCases(solutionDir, caseStructure, baseCase, postDir="postProcessing"):
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
    if caseStructure is None:
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


def get_header(file):
    with open(file, "r") as f:
        lines = [f.readline().strip() for i in range(20)]

    last_comment = max(loc for loc, val in enumerate(lines) if "#" in val)

    columns = lines[last_comment]
    for remove_char in "()#":
        columns = columns.replace(remove_char, "")

    return columns.split()


def load_df(
    solutionFile,
    case_parameters,
    time: float = None,
    apply_func=None,
    category_names: List[str] = None,
    columnNames=None,
    header_from_file=False,
):
    if not os.path.exists(solutionFile):
        return None

    # check if file has braces
    with open(solutionFile, "r") as f:
        lines = [f.readline().strip() for i in range(20)]

    has_brace = "(" in "".join(lines)

    # load df
    suffix = os.path.splitext(solutionFile)[1]
    try:
        if suffix == ".csv":
            df = pd.read_csv(solutionFile)
        elif has_brace:
            df = pd.read_csv(
                solutionFile, comment="#", sep="[() \t]+", engine="python", header=None
            )

            if pd.isnull(df.iloc[0, -1]):
                last_col_name = df.columns[-1]
                df = df.drop(last_col_name, axis=1)
        else:
            df = pd.read_csv(
                solutionFile, comment="#", delim_whitespace=True, header=None
            )
    except pd.errors.EmptyDataError:
        print(f"Note: {solutionFile} was empty. Skipping.")
        return None
    if apply_func is not None:
        if time is None:
            raise ValueError("time needs to be passed if the apply function is passed")
        df = apply_func(case_parameters, time, df)

    # set column names
    if columnNames:
        df.columns = columnNames
    elif header_from_file:
        header = get_header(solutionFile)
        if len(header) == len(df.columns):
            df.columns = get_header(solutionFile)

    # set categories
    for i, variables in enumerate(case_parameters):
        cat_name = "var_" + str(i)
        if category_names:
            cat_name = category_names[i]
        df[cat_name] = variables

    return df


def time_series(
    solutionDir,
    file,
    caseStructure=None,
    baseCase=".",
    columnNames=None,
    set_index=True,
    header_from_file=False,
):
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

    dfs = []
    for i, caseComb in enumerate(caseCombs):
        currentSolutionFile = os.path.join(cases[i], file)
        currentDataFrame = load_df(
            currentSolutionFile, caseComb, header_from_file=header_from_file
        )
        if currentDataFrame is not None:
            if set_index:
                currentDataFrame = currentDataFrame.set_index(
                    currentDataFrame.columns[0]
                )
                currentDataFrame.index.name = "t"
            dfs.append(currentDataFrame)
    outputDf = pd.concat(dfs, axis=0)

    return outputDf


def positional_field(
    solutionDir,
    file,
    time,
    caseStructure=None,
    baseCase=".",
    columnNames=None,
    header_from_file=False,
):
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

    dfs = []
    for i, caseComb in enumerate(caseCombs):
        currentSolutionFile = os.path.join(cases[i], str(time), file)
        currentDataFrame = load_df(
            currentSolutionFile, caseComb, header_from_file=header_from_file
        )
        if currentDataFrame is not None:
            dfs.append(currentDataFrame)
    outputDf = pd.concat(dfs, axis=0)

    return outputDf


def profiling(
    time, processorDir="", caseStructure=None, baseCase=".", file="profiling"
):
    """Load positionalField(surfaces and sets).

    Loads a positionalField of a given case and save them into one
    pandas.DataFrame. multiple cases can be combined with the caseStructure
    argument

    Parameters
    ----------
    time : float
        Point of time at which to load the field.
    processorDir : str, optional
        Solution directory in the OpenFOAM case ``postProcessing`` directory.
        Root directory of all cases.
    file : str, optional
        File name of the solution file.
    caseStructure : list, optional
        List of parent, child and grandchild names::

            [[parent1, parent2],
             [child1, child2, child3],
             [grandchild1, grandchild2]]
    baseCase : str, optional

    Returns
    -------
    outputDf : pandas.DataFrame
        pandas.DataFrame with solutions for all times.

    """
    outputDf = pd.DataFrame()
    cases, caseCombs = getCases("", caseStructure, baseCase, postDir=processorDir)

    dfs = []
    for i, caseComb in enumerate(caseCombs):
        currentSolutionFile = os.path.join(cases[i], str(time), "uniform", file)
        if os.path.exists(currentSolutionFile):
            try:
                prof = ParsedParameterFile(currentSolutionFile)
                currentDataFrame = pd.DataFrame(prof["profiling"]).T
                currentDataFrame = currentDataFrame.reset_index(drop=True)
            except pd.errors.EmptyDataError:
                print("Note: {} was empty. Skipping.".format(currentSolutionFile))
                continue
            counter = 0
            for variables in caseComb:
                currentDataFrame["var_" + str(counter)] = variables
                counter += 1

            dfs.append(currentDataFrame)
    outputDf = pd.concat(dfs, axis=0)

    return outputDf


def posField_to_timeSeries(
    solutionDir,
    file,
    postFunction,
    caseStructure=None,
    baseCase=".",
    header_from_file=False,
    **kwargs,
):
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

    dfs = []
    for i, caseComb in enumerate(caseCombs):
        times = os.listdir(cases[i])

        for time in times:
            currentSolutionFile = os.path.join(cases[i], time, file)
            surfaceDataFrame = load_df(
                currentSolutionFile,
                caseComb,
                time=float(time),
                apply_func=postFunction,
                header_from_file=header_from_file,
                **kwargs,
            )

            dfs.append(surfaceDataFrame)
    outputDf = pd.concat(dfs, axis=0)

    return outputDf
