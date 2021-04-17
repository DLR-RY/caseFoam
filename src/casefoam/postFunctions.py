"""User postprocessing functions.

User function to manipulate the solution data ``['x', 'y', 'z', 'values']``.
The function must return a pandas.DataFrame and the function has to take
the parameters ``(caseComb, time, currentDataFrame, outputDf)``:

>>> def userFunction(caseComb, time, currentDataFrame):
    t = time
    minimum = currentDataFrame.iloc[:, 1].min()
    mean = currentDataFrame.iloc[:, 1].mean()
    maximum = currentDataFrame.iloc[:, 1].max()
    df = pd.DataFrame(np.array([time, minimum, mean, maximum], ndmin=2),
    columns=['time', 'min', 'mean', 'max'])
    df = df.set_index('time')
    return df

"""

import numpy as np
import pandas as pd


def getFreeSurfaceWallAndCentre(caseComb, time, currentDataFrame, axis=0):
    """Return the max, min and mean of the given axis.

    Axis argument can be given as keyword argument in posField_to_timeSeries
    .e.g (axis=1).

    """
    t = time
    minimum = currentDataFrame.iloc[:, axis].min()
    mean = currentDataFrame.iloc[:, axis].mean()
    maximum = currentDataFrame.iloc[:, axis].max()
    df = pd.DataFrame(np.array([time, minimum, mean, maximum], ndmin=2),
                      columns=['time', 'min', 'mean', 'max'])
    df = df.set_index('time')

    return df


def getRadius(caseComb, time, currentDataFrame):
    """Return the max, min and mean of the radius."""
    r = np.sqrt(currentDataFrame.iloc[:, 0]**2 +
                currentDataFrame.iloc[:, 1]**2 +
                currentDataFrame.iloc[:, 2]**2)

    df = pd.DataFrame(np.array([time, r.min(), r.mean(), r.max()],
                               ndmin=2),
                      columns=['time', 'min', 'mean', 'max'])
    df = df.set_index('time')

    return df
