# pytest has to be run from project root directory!
from unittest import case
import casefoam
import os
from casefoam.genCases import Category, OF_Dict, String, Category_Data, ParameterStudy, CaseData, study_structure
from casefoam.utility import of_cases
import itertools
# generate testPostProcessing cases
def test_buildCase():
    # directory of the base case
    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    c1 = Category(
        name="var_0",
        instructions=[OF_Dict(file_name="0/U", entry="boundary/inlet/value")],
    )
    c2 = Category(
        name="var_1",
        instructions=[OF_Dict(file_name="0/T", entry="boundary/inlet/value")],
    )
    c3 = Category(
        name="var_2",
        instructions=[OF_Dict(file_name="0/p", entry="boundary/inlet/value")],
    )
    c4 = Category(
        name="var_3",
        instructions=[String(file_name='system/stringTest.txt', entry="STRINGMARKER")],
    )

    U = [Category_Data(cat_name=f"Ux{i}",values=[i]) for i in [1,3]]
    T = [Category_Data(cat_name=f"T{i}",values=[i]) for i in [1]]
    p = [Category_Data(cat_name=f"p{i}",values=[i]) for i in [1]]
    string = [Category_Data(cat_name=f"string{i}",values=[i]) for i in [10]]

    cases_data = list(itertools.product(U,T,p,string))
    cases_data = [CaseData(case_data=[i,j,k,l]) for i,j,k,l in cases_data]# print()a=case_data())

    p1 = ParameterStudy(base_case="testCase",categories=[c1,c2,c3,c4],study_data=cases_data)

    study_structure(p1)

    os.chdir(cwd)


def test_checkFiles():
    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    of_cases = casefoam.of_cases("Cases")
    assert "Cases/Ux3/T1/p1/string10" in of_cases
    assert "Cases/Ux1/T1/p1/string10" in of_cases

    # assert "rmCases" in os.listdir()
    # assert "Allrun" in os.listdir()
    # assert "Allclean" in os.listdir()
    assert "Cases" in os.listdir()

    os.chdir(cwd)
