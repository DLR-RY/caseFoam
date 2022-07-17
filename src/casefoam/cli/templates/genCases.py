from casefoam.genCases import (
    create_category,
    String,
    OF_Dict,
    create_study_structure,
    create_category_data,
)

baseCase = "REPLACE_CASE"

cat_1 = create_category(
    cat_name="some_var",
    instructions=[String(file_name="system/simulationParameters", entry="some_var")],
)
cat_2 = create_category(
    cat_name="Res",
    instructions=[
        OF_Dict(file_name="system/simulationParameters", entry="deltax"),
        OF_Dict(file_name="system/simulationParameters", entry="deltay"),
    ],
)


grid_data = [[10, 10], [20, 20], [30, 30]]

cat_data_1 = create_category_data(grid_data, cat_names=["grid1", "grid2", "grid3"])
cat_data_2 = create_category_data(
    ["0.2", "0.3", "0.4"], cat_names=["var_02", "var_03", "var_04"]
)

create_study_structure(
    base_case=baseCase, categories=[cat_1, cat_2], study_data=[cat_data_1, cat_data_2]
)
