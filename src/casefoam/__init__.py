"""
CaseFOAM - a OpenFOAM case manipulatior and creator.

This module is a addition to PyFoam and can setup automatically OpenFOAM cases
with variating conditions.
"""
from casefoam.core import *
from casefoam.mkCases import *
from casefoam import utility
from casefoam.loadData import *
from casefoam.postFunctions import *
from casefoam.utility import of_cases

__version__ = '0.2.0'
