import casefoam

baseCase = 'damBreak'
caseStructure = [['height_02', 'height_03', 'height_04'],
                 ['grid1', 'grid2', 'grid3']]

def update_grid(a, b, c, d, e):
    return {
        'system/blockMeshDict': {'#!stringManipulation': {'varA': '%s' % a,
                                                          'varB': '%s' % b,
                                                          'varC': '%s' % c,
                                                          'varD': '%s' % d,
                                                          'varE': '%s' % e}}
    }


def update_height(height):
    return {
        'system/setFieldsDict': {'#!stringManipulation':
                                 {'var_height': '%s' % height}}
    }


caseData = {
    'height_02': update_height(0.2),
    'height_03': update_height(0.3),
    'height_04': update_height(0.4),
    'grid1': update_grid(23, 8, 19, 42, 4),
    'grid2': update_grid(23*2, 8*2, 19*2, 42*2, 4*2),
    'grid3': update_grid(23*3, 8*3, 19*3, 42*3, 4*3)
}

# generate cases
casefoam.mkCases(baseCase, caseStructure, caseData, hierarchy='tree',
                 writeDir='Cases')
