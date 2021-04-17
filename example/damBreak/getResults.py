from casefoam import time_series, positional_field
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import casefoam
import numpy as np

caseStructure = [['height_02', 'height_03', 'height_04'],
                 ['grid1', 'grid2', 'grid3']]
baseCase = 'Cases'
probeDir = 'probes/0'
surfaceDir = 'freeSurface'
setDir = 'sample1'

# load probe data
p = time_series(probeDir, 'p', caseStructure, baseCase)
T = time_series(probeDir, 'T', caseStructure, baseCase)
U = time_series(probeDir, 'U', caseStructure, baseCase)
p = p.reset_index()
T = T.reset_index()
U = U.reset_index()

sns.lineplot(x='t',y=1,hue='var_0',style='var_1',data=p)
plt.xlabel('Time $t$')
plt.ylabel('Pressure $p$')

# load surface data
surf = positional_field(surfaceDir, 'p_freeSurface.raw', 0.1, caseStructure, baseCase)

plt.figure()
sns.scatterplot(x=0,y=1,hue='var_0',style='var_1',data=surf)
plt.xlabel('x [m]')
plt.ylabel('y [m]')


# # load set data
centerLine = positional_field(setDir, 'centreLine_T.xy',0.1, caseStructure, baseCase)

plt.figure()
sns.lineplot(x=0,y=1,hue='var_0',style='var_1',data=centerLine)
plt.xlabel('x [m]')
plt.ylabel('T [K]')

# # plot forces
forcesDir = 'forces/0'
forces = time_series(forcesDir, 'force.dat', caseStructure, baseCase)
forces = forces.reset_index()

plt.figure()
sns.lineplot(x='t',y=1,hue='var_0',style='var_1',data=forces)
plt.xlabel('x [m]')
plt.ylabel('F [N]')

def max_min_Height(caseComb, time, currentDataFrame):
    t = time
    minimum = currentDataFrame.iloc[:, 1].min()
    maximum = currentDataFrame.iloc[:, 1].max()
    df = pd.DataFrame(np.array([time, minimum, maximum],
                      ndmin=2),
                      columns=['time', 'min', 'max'])
    df = df.set_index('time')
    return df

surf_Heights = casefoam.posField_to_timeSeries(
    surfaceDir, 'p_freeSurface.raw', max_min_Height, caseStructure, baseCase)
surf_Heights = surf_Heights.reset_index()

plt.figure()
sns.lineplot(x='time',y='max',hue='var_0',style='var_1',data=surf_Heights)
plt.xlabel('x [m]')
plt.ylabel('h [m]')
plt.show()
