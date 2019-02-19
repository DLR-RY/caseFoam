# pytest has to be run from project root directory!
import casefoam
import os


# generate testPostProcessing cases
def test_probeSolution():
    try:
        cwd = os.getcwd()
        casedir = "tests/testPostProcessing"
        cmd_make = "python mkPostProcessing.py"
        cmd_rm = "./rmCases"
        os.chdir(casedir)
        os.system(cmd_make)

        # load probe solutions
        solutionDir = "probes"
        file = "probeData"
        caseStructure = [['Ux1', 'Ux3'],
                         ['T1'],
                         ['p1'],
                         ['string10']]
        baseCase = "testPostProcessing"

        casefoam.loadProbeSolutions(solutionDir, file, caseStructure,
                                    baseCase)

        os.system(cmd_rm)
        os.chdir(cwd)
    except all:
        raise AssertionError
