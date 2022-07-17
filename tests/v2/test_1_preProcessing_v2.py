# pytest has to be run from project root directory!
from sys import prefix
from unittest import case
import casefoam
import os
from casefoam.genCases import (
    Category,
    OF_Dict,
    String,
    Category_Data,
    create_category,
    create_category_data,
    create_study_structure
)
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
    c2 = create_category(
        cat_name="var_1",
        instructions=[OF_Dict(file_name="0/T", entry="boundary/inlet/value")],
    )  # positional arguments also work
    c3 = create_category(
        cat_name="var_2",
        instructions=[{"file_name": "0/p", "entry": "boundary/inlet/value"}],
    )
    c4 = create_category(
        cat_name="var_3",
        instructions=[String(file_name="system/stringTest.txt", entry="STRINGMARKER")],
    )

    U = create_category_data(data=[1, 3], prefix="Ux")  # list of change parameters
    T = create_category_data(data=[1], cat_names=["T1"])
    p = [Category_Data(cat_name=f"p{i}", values=[i]) for i in [1]]  #
    string = create_category_data(data=[10], cat_names=["string10"])

    create_study_structure(
        base_case="testCase", categories=[c1, c2, c3, c4], study_data=[U, T, p, string]
    )

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
