from casefoam.genCases import (
    String,
    OF_Dict,
    Bash_Cmd,
    ParaStudy,
)


def grid_vars(factor):
    l = [23 * factor, 4 * factor]
    return list(map(str, l))

# base case for the generation of the other cases
ps = ParaStudy(base_case="REPLACE_CASE")

# add Parameters and what to change from the base case
p_1 = ps.add_parameter(
    "p_1",
    modify=[String(file_name="system/setFieldsDict", entry="some_value")],
)
Res = ps.add_parameter(
    "Res",
    modify=[
        OF_Dict(file_name="system/simulationParameters", entry="deltax"),
        OF_Dict(file_name="system/simulationParameters", entry="deltay"),
    ],
)

# add parameter inputs 
# specify the name of the input and the value 
p_1["height_02"] = "0.2"
p_1["height_03"] = "0.3"
p_1["height_04"] = "0.4"

res_data = {
    "grid1": grid_vars(1),
    "grid2": grid_vars(2),
    "grid3": grid_vars(3),
}
Res.set_inputs(res_data)

# case are created with the cartesian product aka every possible 
# parameter input is varied
# create the nine modified cases
ps.create_study()
