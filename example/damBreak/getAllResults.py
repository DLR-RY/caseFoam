from casefoam import loadProbeSolutions, loadSurfaceSolution, loadSetSolution
import matplotlib.pyplot as plt
import pandas as pd
import casefoam

caseStructure = [['grid1', 'grid2', 'grid3']]
baseCase = 'damBreak'
probeDir = 'probes/0'
surfaceDir = 'freeSurface'
setDir = 'sample1'

# load probe data
p = loadProbeSolutions(probeDir, 'p', caseStructure, baseCase)
T = loadProbeSolutions(probeDir, 'T', caseStructure, baseCase)
U = loadProbeSolutions(probeDir, 'U', caseStructure, baseCase)
# load surface data


# plot Pressure
p.plot(marker='o', ls='')
plt.xlabel('Time $t$')
plt.ylabel('Pressure $p$')
plt.tight_layout()
plt.show()


# plot surface at 0.1 seconds
surf = loadSurfaceSolution(surfaceDir, 'p_freeSurface.raw', caseStructure,
                           baseCase, 0.1)

plt.figure()
idx = pd.IndexSlice
plt.plot(surf.loc[:, idx[:, 'x']], surf.loc[:, idx[:, 'y']], marker='o', ls='')
plt.xlabel('$x$')
plt.ylabel('$y$')
plt.tight_layout()
plt.show()

# plot temperature at ther centre line at 0.1 seconds
# load set data
centerLine = loadSetSolution(setDir, 'centreLine_T.xy', caseStructure,
                             baseCase, 0.1)

plt.figure()
plt.plot(centerLine.loc[:, idx[:, 'axis']], centerLine.loc[:, idx[:, 'value']],
         marker='o', ls='')
plt.xlabel('Position $x$')
plt.ylabel('Temperature $T$')
plt.tight_layout()
plt.show()

# plot forces
forcesDir = 'forces/0'
forces = casefoam.loadForces(forcesDir, 'force.dat', caseStructure, baseCase)
forces = forces.interpolate()  # linear interpolation between index
plt.figure()
forces.loc[:, idx[:, 0]].plot()
plt.xlabel('Time $t$')
plt.ylabel('Force $F$')
plt.tight_layout()
plt.show()
