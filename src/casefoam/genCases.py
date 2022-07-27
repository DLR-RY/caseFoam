from typing_extensions import Annotated
from typing import Literal, Union, List, Any, Dict, Tuple, Optional, Callable
from pathlib import Path
import shutil, os
import itertools
import subprocess
from enum import Enum
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from pydantic import BaseModel, Field, validator

# Modifiers
class OF_Dict(BaseModel):
    file_name: Union[str, Path] = Field(default="system/simulationParameters")
    entry: str
    instruction_type: Literal["of_dict"] = Field(default="of_dict")

    def _nested_set(self, dic: Dict, keyword: str, value: Any):
        key_list = keyword.split("/")
        key_list[:] = [x for x in key_list if x]
        if len(key_list) == 1:
            dic[key_list[-1]] = value
            return
        for key in key_list[:-1]:
            if key not in dic:
                raise ValueError(
                    f"""
                    key not found in dictionary
                    valid options: {dic.keys()}
                    given: {key}
                """
                )  # Keyerror ignore line breaks
            dic = dic[key]
        dic[key_list[-1]] = value

    def execute(self, value: Any):
        ppp = ParsedParameterFile(self.file_name)
        self._nested_set(ppp.content, self.entry, value)
        ppp.writeFile()


class String(BaseModel):
    file_name: Union[str, Path]
    entry: str
    instruction_type: Literal["string"] = Field(default="string")

    def execute(self, value: str):
        file = Path(self.file_name)
        f_content = file.read_text()
        f_content = f_content.replace(self.entry, value)
        file.write_text(f_content)


class Bash_Cmd(BaseModel):
    instruction_type: Literal["bash_cmd"] = Field(default="bash_cmd")

    def execute(self, value: str):
        subprocess.call(value, shell=True)


Modifiers = Annotated[
    Union[OF_Dict, String, Bash_Cmd],
    Field(discriminator="instruction_type"),
]


class Parameter(BaseModel):
    name: str
    modifiers: List[Modifiers]

    def execute(self, values: List[Any]):
        for i, instruct in enumerate(self.modifiers):
            instruct.execute(values[i])


class Parameter_Inputs(BaseModel):
    input_name: str
    values: List[Any]


class Case_Inputs(BaseModel):
    case_data: List[Parameter_Inputs]


class CaseModifier(BaseModel):
    parameters: List[Parameter]
    case_data: Case_Inputs

    def execute(self):
        for idx, cat_mod in enumerate(self.parameters):
            cat_mod.execute(self.case_data.case_data[idx].values)


class OFCases(BaseModel):
    cases: List[CaseModifier]

    def execute(self):
        for mod in self.cases:
            mod.execute()


class StructureEnum(str, Enum):
    flat = "flat"
    tree = "tree"


class ParameterStudy(BaseModel):
    base_case: Union[str, Path]
    writeDir: Union[str, Path] = Field(default="Cases")
    structure: StructureEnum = StructureEnum.tree
    parameters: List[Parameter]
    para_inputs: List[Case_Inputs]

    @validator("para_inputs")
    def verify_data(cls, v, values, **kwargs):
        nParameters = len(values["parameters"])
        nInputs_in_parameters = [len(val.modifiers) for val in values["parameters"]]
        if not all([len(d.case_data) == nParameters for d in v]):
            nInput_data = [len(d.case_data) for d in v]
            raise ValueError(
                f"""
                    number of provided categories: {nParameters}
                    number of provided inputs: min: {min(nInput_data)} max: {min(nInput_data)}
                    They have to match!
                 """
            )
        for d in v:
            nValues = [len(val.values) for val in d.case_data]
            if nValues != nInputs_in_parameters:
                raise ValueError(
                    f"""
                        number of modifies: {nInputs_in_parameters}
                        number of inputs: {nValues}
                        They have to match!
                    """
                )
        ## more validation are the cat names unique
        return v


def create_cases(ps: ParameterStudy) -> OFCases:
    cases = []
    cats = ps.parameters
    for cs in ps.para_inputs:
        cases.append(CaseModifier(parameters=cats, case_data=cs))
    return OFCases(cases=cases)


def get_cat_names(ps: ParameterStudy) -> List[str]:
    return [c.name for c in ps.parameters]


def case_variations(cases: OFCases) -> List[List[str]]:
    vars = []
    for c in cases.cases:
        vars.append([d.input_name for d in c.case_data.case_data])
    return vars


def case_struct(
    cvs: List[List[str]],
    writeDir: Union[str, Path] = "Cases",
    structure: StructureEnum = StructureEnum.tree,
) -> List[Path]:
    if structure == "tree":
        cs = [Path(writeDir, "/".join(cv)) for cv in cvs]
    else:
        cs = [Path(writeDir, "-".join(cv)) for cv in cvs]
    return cs


def create_parameter(
    para_name: str,
    modify: List[Union[Dict[str, Any], Union[OF_Dict, String, Bash_Cmd]]],
) -> Parameter:

    if type(modify[0]) != dict:
        return Parameter(name=para_name, modifiers=modify)

    # add default values for the case that a list of dict is supplied
    for i in modify:
        if "instruction_type" not in i:
            i["instruction_type"] = "of_dict"
        if i["instruction_type"] == "of_dict":
            if "file_name" not in i:
                i["file_name"] = "system/simulationParameters"

    return Parameter(name=para_name, modifiers=modify)


Para_input_func = Callable[
    [int, Union[Any, List[Any]], Optional[List[str]]], Tuple[str, List[Any]]
]


def para_input_modfunc(
    idx: int,
    data: Union[Any, List[Any]],
    input_names: Optional[List[str]] = None,
    prefix: str = "c_",
) -> Tuple[str, List[Any]]:
    if input_names != None:
        if type(data) == list:
            return input_names[idx], data
        else:
            return input_names[idx], [data]
    if type(data) == str:
        return data, [data]
    elif type(data) == list:
        return f"{prefix}{idx}", data
    else:  # assume integer float etc
        return f"{prefix}{data}", [data]


def create_parameter_input(
    data: List[Any],
    input_names: Optional[List[str]] = None,
    modifier: Para_input_func = para_input_modfunc,
    **kwargs,
) -> List[Parameter_Inputs]:
    cat_data = []
    for idx, d in enumerate(data):
        input_name, values = para_input_modfunc(idx, d, input_names, **kwargs)
        cat_data.append(Parameter_Inputs(input_name=input_name, values=values))
    return cat_data


def create_case_inputs(
    study_data: List[List[Parameter_Inputs]], cartesian: bool = True
) -> List[Case_Inputs]:
    if not cartesian:
        cases_data = [Case_Inputs(case_data=c) for c in case_variations]
        return cases_data

    case_variations = list(itertools.product(*study_data))
    cases_data = [Case_Inputs(case_data=c) for c in case_variations]
    return cases_data


def _create_study_structure(ps: ParameterStudy) -> None:
    cases = create_cases(ps)
    case_vars = case_variations(cases)

    with open(Path("para_study.json"), "w") as f:
        f.write(ps.json(indent=2))

    dir_cases = case_struct(case_vars, writeDir=ps.writeDir, structure=ps.structure)

    for c, d in zip(cases.cases, dir_cases):
        shutil.copytree(ps.base_case, d)
        with open(Path(d, "case.json"), "w") as f:
            f.write(c.json(indent=2))

    pwd = os.getcwd()
    for c, d in zip(cases.cases, dir_cases):
        os.chdir(Path(pwd, d))
        c.execute()

    os.chdir(pwd)


def create_study_structure(
    base_case: Union[str, Path],
    parameters: List[Parameter],
    case_inputs: Union[List[Case_Inputs], List[List[Parameter_Inputs]]],
    writeDir: Union[str, Path] = "Cases",
    structure: StructureEnum = StructureEnum.tree,
    cartesian: bool = True,
) -> None:
    """creates the case structure for the parameter study


    Parameters
    ----------
        base_case (Union[str, Path]):
            Directory of the base case that is modified to create the parameter study
        categories (List[Category]):
            category with instructions
        study_data (Union[List[CaseData], List[List[Category_Data]]]):
             data of the category
        writeDir (Union[str, Path], optional):
            Directory where created cases are stored.
        structure ({'flat', 'tree'}, optional):
            Hierarchy in which the case directory will be created.

            * 'flat': Creates the structure `parent_child_grandchild`.
            * 'tree': Creates the structure `parent/child/grandchild`. Defaults to "Cases".
        cartesian (bool, optional) Defaults to True. :
            cartesian product of all categories. Defaults to True.
    """
    if type(case_inputs[0]) != Case_Inputs:
        case_inputs = create_case_inputs(case_inputs, cartesian)

    ps = ParameterStudy(
        base_case=base_case,
        writeDir=writeDir,
        structure=structure,
        parameters=parameters,
        para_inputs=case_inputs,
    )
    _create_study_structure(ps)


class ParaStudy_Data:
    def __init__(
        self, para_name, modifiers: Parameter, data: List[Parameter_Inputs] = None
    ):
        self.para_name = para_name
        self.modifiers: Parameter = modifiers
        self.data: List[Parameter_Inputs] = data

    def __setitem__(self,input_name,values):
        if self.data is None:
            self.data = []
        if type(values) is not list:
            values = [values]
        self.data.append(Parameter_Inputs(input_name=input_name,values=values))

    def set_inputs(
        self,
        value_dict: Dict[str,List[Any]]
    ) -> "ParaStudy_Data":
        for k,v in value_dict.items():
            self.__setitem__(k,v)
        return self


class ParaStudy:
    def __init__(self, base_case):
        self.base_case = base_case
        self._parameters: List[ParaStudy_Data] = None

    def add_parameter(
        self,
        name: str,
        modify: List[
            Union[Dict[str, Any], Union[OF_Dict, String, Bash_Cmd]]
        ],
        data: List[Parameter_Inputs] = None,
    ) -> "ParaStudy_Data":
        if self._parameters is None:
            self._parameters = []
        mods =  create_parameter(para_name=name,modify=modify)
        p = ParaStudy_Data(name, modifiers=mods, data=data)

        self._parameters.append(p)

        return self._parameters[-1]

    def parameter(self, name: str) -> "ParaStudy_Data":
        for p in self._parameters:
            if p.para_name == name:
                return p
        raise KeyError("parameter not found")

    def create_study(self) -> None:
        # validate
        create_study_structure(
            base_case=self.base_case,
            parameters=[i.modifiers for i in self._parameters],
            case_inputs=[i.data for i in self._parameters],
        )
