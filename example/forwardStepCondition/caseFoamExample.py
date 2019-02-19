import casefoam

# directory of the base case
baseCase = 'forwardStepCondition'

# list of parent, child and grandchild names
caseStructure = [['Ux1', 'Ux2'],
                 ['string10', 'string20']]


# dictionarys with data for the caseData dictionary
update_Ux1 = {
    '0/U': {'boundaryField': {'inlet': {'value': 'uniform (1 0 0)'}}}
}

update_Ux2 = {
    '0/U': {'boundaryField': {'inlet': {'value': 'uniform (2 0 0)'}}}
}

update_string10 = {
    'Ux1': {
        'system/stringTest.txt': {
            '#!stringManipulation': {'STRINGMARKER': 'Ux1 10'}
        }
    },
    'Ux2': {
        'system/stringTest.txt': {
            '#!stringManipulation': {'STRINGMARKER': 'Ux2 10'}
        }
    },
}

update_string20 = {
    'Ux1': {
        'system/stringTest.txt': {
            '#!stringManipulation': {'STRINGMARKER': 'Ux1 20'}
        }
    },
    'Ux2': {
        'system/stringTest.txt': {
            '#!stringManipulation': {'STRINGMARKER': 'Ux2 20'}
        }
    },
}


# dictionary of data to update
caseData = {'Ux1': update_Ux1,
            'Ux2': update_Ux2,
            'string10': update_string10,
            'string20': update_string20}

# generate cases
casefoam.mkCases(baseCase, caseStructure, caseData, hierarchy='tree')
