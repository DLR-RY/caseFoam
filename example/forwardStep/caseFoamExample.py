import casefoam

# directory of the base case
baseCase = 'forwardStep'

# list of parent, child and grandchild names
caseStructure = [['Ux1', 'Ux2', 'Ux3'],
                 ['T1', 'T2', 'T3', 'T4'],
                 ['p1', 'p2'],
                 ['string10', 'string20']]


# dictionarys with data for the caseData dictionary
update_Ux1 = {
    '0/U': {'boundaryField': {'inlet': {'value': 'uniform (1 0 0)'}}}}

update_Ux2 = {
    '0/U': {'boundaryField': {'inlet': {'value': 'uniform (2 0 0)'}}}}

update_Ux3 = {
    '0/U': {'boundaryField': {'inlet': {'value': 'uniform (3 0 0)'}}}}

update_T1 = {
    '0/T': {'boundaryField': {'inlet': {'value': 'uniform 1'}}}}

update_T2 = {
    '0/T': {'boundaryField': {'inlet': {'value': 'uniform 2'}}}}

update_T3 = {
    '0/T': {'boundaryField': {'inlet': {'value': 'uniform 3'}}}}

update_T4 = {
    '0/T': {'boundaryField': {'inlet': {'value': 'uniform 4'}}}}

update_p1 = {
    '0/p': {'boundaryField': {'inlet': {'value': 'uniform (1 0 0)'}}},
    'system/controlDict': {'application': 'rhoCentralDyMFoam'}}

update_p2 = {
    '0/p': {'boundaryField': {'inlet': {'value': 'uniform (2 0 0)'}}}}

update_string10 = {
    'system/stringTest.txt': {'#!stringManipulation': {'STRINGMARKER': '10'}}}

update_string20 = {
    'system/stringTest.txt': {'#!stringManipulation': {'STRINGMARKER': '20'}}}


# dictionary of data to update
caseData = {'Ux1': update_Ux1,
            'Ux2': update_Ux2,
            'Ux3': update_Ux3,
            'T1': update_T1,
            'T2': update_T2,
            'T3': update_T3,
            'T4': update_T4,
            'p1': update_p1,
            'p2': update_p2,
            'string10': update_string10,
            'string20': update_string20}

# generate cases
casefoam.mkCases(baseCase, caseStructure, caseData, hierarchy='tree')
