import casefoam

baseCase = 'damBreak'
caseStructure = [['height_02', 'height_03', 'height_04'],
                 ['grid1', 'grid2', 'grid3']
                ]

#update_grid1 = {
#    'system/blockMeshDict': {'#!stringManipulation': {'varA': '23',
#                                                      'varB': '8',
#                                                      'varC': '19',
#                                                      'varD': '42',
#                                                      'varE': '4'}},
#}
#
#update_grid2 = {
#    'system/blockMeshDict': {'#!stringManipulation': {'varA': '46',
#                                                      'varB': '16',
#                                                      'varC': '38',
#                                                      'varD': '84',
#                                                      'varE': '8'}},
#}
#
#update_grid3 = {
#    'system/blockMeshDict': {'#!stringManipulation': {'varA': '69',
#                                                      'varB': '24',
#                                                      'varC': '57',
#                                                      'varD': '126',
#                                                      'varE': '12'}},
#}

def update_grid(a,b,c,d,e):
    return {
        'system/blockMeshDict': {'#!stringManipulation': {'varA': '%s' %a,
                                                        'varB': '%s' %b,
                                                        'varC': '%s' %c,
                                                        'varD': '%s' %d,
                                                        'varE': '%s' %e}}
    }
    
def update_height(height):
    return {
        'system/setFieldsDict': {'#!stringManipulation':
                                {'var_height': '%s' %height}}
    }

caseData = {
    'height_02': update_height(0.2),
    'height_03': update_height(0.3),
    'height_04': update_height(0.4),
    'grid1': update_grid(23,8,19,42,4),
    'grid2': update_grid(23*2,8*2,19*2,42*2,4*2),
    'grid3': update_grid(23*3,8*3,19*3,42*3,4*3)
}

# generate cases
casefoam.mkCases(baseCase, caseStructure, caseData, hierarchy='tree',writeDir='Cases')