# pytest has to be run from project root directory!
import casefoam
import os

# generate testPostProcessing cases
def test_buildCase():
    # directory of the base case

    baseCase = 'testCase'
    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    # list of parent, child and grandchild names
    caseStructure = [['Ux1', 'Ux3'],
                     ['T1'],
                     ['p1'],
                     ['string10']]

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
        '0/p': {'boundaryField': {'inlet': {'value': 'uniform (1 0 0)'}}}}

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
    casefoam.mkCases(baseCase, caseStructure, caseData,
                     hierarchy='tree', writeDir='Cases')

    os.chdir(cwd)

def test_checkFiles():
    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    assert 'rmCases' in os.listdir()
    assert 'Allrun' in os.listdir()
    assert 'Allclean' in os.listdir()
    assert 'Cases' in os.listdir()

    os.chdir(cwd)



