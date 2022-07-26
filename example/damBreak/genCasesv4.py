from casefoam.genCases import String, ParaStudy


ps = ParaStudy("damBreak")

# add height parameter
(
    ps.add_parameter("height")
    .set_modifiers([String("system/setFieldsDict", "var_height")])
    .set_data(["0.2", "0.3", "0.4"], cat_names=["height_02", "height_03", "height_04"])
)

# add Resolution parameter
def grid_vars(factor):
    l = [23 * factor, 8 * factor, 19 * factor, 42 * factor, 4 * factor]
    return list(map(str, l))



Res = ps.add_parameter("Res")
Res.set_modifiers(
    [
        String("system/blockMeshDict", e)
        for e in ["varA", "varB", "varC", "varD", "varE"]
    ]
)
grid_data = [grid_vars(1), grid_vars(2), grid_vars(3)]
Res.set_data(grid_data, cat_names=["grid1", "grid2", "grid3"])


# create the modified cases
ps.create_study()
