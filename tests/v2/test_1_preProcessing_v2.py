# pytest has to be run from project root directory!
from sys import prefix
from unittest import case
import casefoam
import os
import shutil
from casefoam.genCases import (
    ParaStudy,
    Parameter,
    OF_Dict,
    String,
    Parameter_Inputs,
    create_parameter,
    create_parameter_input,
    create_study_structure,
    ParaStudy
)
from casefoam.utility import of_cases
import itertools

# generate testPostProcessing cases
def test_buildCase_with_funcs():
    # directory of the base case
    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    c1 = Parameter(
        name="var_0",
        modifiers=[OF_Dict(file_name="0/U", entry="boundaryField/inlet/value")],
    )
    c2 = create_parameter(
        para_name="var_1",
        modify=[OF_Dict(file_name="0/T", entry="boundaryField/inlet/value")],
    )  # positional arguments also work
    c3 = create_parameter(
        para_name="var_2",
        modify=[{"file_name": "0/p", "entry": "boundaryField/inlet/value"}],
    )
    c4 = create_parameter(
        para_name="var_3",
        modify=[String(file_name="system/stringTest.txt", entry="STRINGMARKER")],
    )

    U = create_parameter_input(data=[1, 3], prefix="Ux")  # list of change parameters
    T = create_parameter_input(data=[1], input_names=["T1"])
    p = [Parameter_Inputs(input_name=f"p{i}", values=[i]) for i in [1]]  #
    string = create_parameter_input(data=["10"], input_names=["string10"])

    create_study_structure(
        base_case="testCase", parameters=[c1, c2, c3, c4], case_inputs=[U, T, p, string]
    )

    os.chdir(cwd)

def test_removeCases():

    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    shutil.rmtree('Cases')

    # assert 'rmCases' not in os.listdir()
    # assert 'Allrun' not in os.listdir()
    # assert 'Allclean' not in os.listdir()
    assert 'Cases' not in os.listdir()

    os.chdir(cwd)

def test_buildCase():
    # directory of the base case
    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    ps = ParaStudy("testCase")

    U = ps.add_parameter(
        name="var_0",
        modify=[OF_Dict(file_name="0/U", entry="boundaryField/inlet/value")],
    )
    T = ps.add_parameter(
        name="var_1",
        modify=[OF_Dict(file_name="0/T", entry="boundaryField/inlet/value")],
    )  # positional arguments also work
    p = ps.add_parameter(
        name="var_2",
        modify=[{"file_name": "0/p", "entry": "boundaryField/inlet/value"}],
    )
    string = ps.add_parameter(
        name="var_3",
        modify=[String(file_name="system/stringTest.txt", entry="STRINGMARKER")],
    )

    U_data = {
        "Ux1": "1",
        "Ux3": ["3"],
    }
    
    U.set_inputs(U_data)
    T["T1"] = "1"
    p["p1"] = "1"
    string["string10"] = "10"


    ps.create_study()

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
