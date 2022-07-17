import fractions
import casefoam
from casefoam.genCases import create_category, String, create_study_structure, create_category_data

baseCase = 'damBreak'

instructions = [String(file_name="system/blockMeshDict",entry=e) for e in ["varA","varB","varC","varD","varE"]]
grid = create_category(cat_name="Res",instructions=instructions)

height = create_category(cat_name="height",instructions=[String(file_name='system/setFieldsDict',entry="var_height")])

def grid_vars(factor):
    l = [23*factor, 8*factor, 19*factor, 42*factor, 4*factor]
    return list(map(str, l))

grid_data = [
    grid_vars(1),
    grid_vars(2),
    grid_vars(3)
]

grids = create_category_data(grid_data,cat_names=['grid1', 'grid2', 'grid3'])
heights = create_category_data(["0.2","0.3","0.4"],cat_names=['height_02', 'height_03', 'height_04'])

create_study_structure(base_case=baseCase,categories=[height, grid],study_data=[heights, grids])
