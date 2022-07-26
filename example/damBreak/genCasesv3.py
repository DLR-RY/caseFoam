from casefoam.genCases import (
    String,
    ParaStudy,
)


def grid_vars(factor):
    l = [23 * factor, 8 * factor, 19 * factor, 42 * factor, 4 * factor]
    return list(map(str, l))


ps = ParaStudy(base_case="damBreak")

# add Parameters
ps.add_parameter("height")
ps.add_parameter("Res")

# set modifies
ps.parameter("height").set_modifiers([String("system/setFieldsDict", "var_height")])
ps.parameter("Res").set_modifiers(
    [
        String("system/blockMeshDict", e)
        for e in ["varA", "varB", "varC", "varD", "varE"]
    ]
)

# set Data
ps.parameter("height").set_data(
    ["0.2", "0.3", "0.4"], cat_names=["height_02", "height_03", "height_04"]
)
grid_data = [grid_vars(1), grid_vars(2), grid_vars(3)]
ps.parameter("Res").set_data(grid_data, cat_names=["grid1", "grid2", "grid3"])

#create the modified cases
ps.create_study()
