from casefoam.genCases import (
    String,
    ParaStudy,
)


def grid_vars(factor):
    l = [23 * factor, 8 * factor, 19 * factor, 42 * factor, 4 * factor]
    return list(map(str, l))


ps = ParaStudy(base_case="damBreak")

# add Parameters with modifiers
fluidHeight = ps.add_parameter(
    "fluidHeight",
    modify=[String(file_name="system/setFieldsDict", entry="var_fluidHeight")],
)
Resolution = ps.add_parameter(
    "Resolution",
    modify=[
        String(file_name="system/blockMeshDict", entry=e)
        for e in ["varA", "varB", "varC", "varD", "varE"] 
    ], # add 5 modifiers that overwrite varA to varE
)

# add parameter inputs
fluidHeight["fluidHeight_02"] = "0.2"
fluidHeight["fluidHeight_03"] = "0.3"
fluidHeight["fluidHeight_04"] = "0.4"

res_data = {
    "grid1": grid_vars(1),
    "grid2": grid_vars(2),
    "grid3": grid_vars(3),
}

Resolution.set_inputs(res_data)

# create the modified cases
ps.create_study()
