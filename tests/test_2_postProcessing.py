# pytest has to be run from project root directory!
import casefoam
from casefoam.postFunctions import getFreeSurfaceWallAndCentre
import os
from subprocess import Popen,PIPE


def test_time_series():
    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    solutionDir = "probes"
    file = "probeData"
    caseStructure = [['Ux1', 'Ux3'],
                        ['T1'],
                        ['p1'],
                        ['string10']]
    baseCase = "Cases"

    df = casefoam.time_series(solutionDir, file, caseStructure,baseCase)

    assert df.index.max() == 1
    assert df[1].max() == 1
    assert df[2].max() == 2
    assert df[3].max() == 3
    assert df[4].max() == 4
    assert df[5].max() == 5
    assert df[6].max() == 6
    assert df[7].max() == 7

    os.chdir(cwd)

def test_forces():
    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    solutionDir = "forces/0"
    file = "force.dat"
    caseStructure = [['Ux1', 'Ux3'],
                        ['T1'],
                        ['p1'],
                        ['string10']]
    baseCase = "Cases"

    F = casefoam.time_series(solutionDir, file, caseStructure,baseCase)

    assert F.index.max() == 1
    assert F[1].max() == 1
    assert F[2].max() == 1
    assert F[3].max() == 1
    assert F[4].max() == 2
    assert F[5].max() == 2
    assert F[6].max() == 2
    assert F[7].max() == 3
    assert F[7].max() == 3
    assert F[7].max() == 3

    os.chdir(cwd)


def test_freeSurface():
    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    solutionDir = "freeSurface"
    file = "p_freeSurface.raw"
    caseStructure = [['Ux1', 'Ux3'],
                        ['T1'],
                        ['p1'],
                        ['string10']]
    baseCase = "Cases"

    surf = casefoam.positional_field(solutionDir, file, 0, caseStructure,baseCase)

    assert surf[3].max() == 0

    os.chdir(cwd)

def test_sample_timeSeries():

    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    solutionDir = "sample1"
    file = "centreLine_T.xy"
    caseStructure = [['Ux1', 'Ux3'],
                        ['T1'],
                        ['p1'],
                        ['string10']]
    baseCase = "Cases"

    surf_time = casefoam.posField_to_timeSeries(solutionDir, file, getFreeSurfaceWallAndCentre, caseStructure,baseCase)

    grouped_df = surf_time.groupby(['var_0','var_1','var_2','var_3'])

    assert len(grouped_df.size()) == 2
    assert surf_time['min'].max() == 0
    assert surf_time['max'].max() == 1

    os.chdir(cwd)


def test_removeCases():

    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    process = Popen(['sh','./rmCases'], stdin=PIPE, stdout=PIPE)
    process.communicate(input=b'y\n')

    assert 'rmCases' not in os.listdir()
    assert 'Allrun' not in os.listdir()
    assert 'Allclean' not in os.listdir()
    assert 'Cases' not in os.listdir()

    os.chdir(cwd)