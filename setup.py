#!/usr/bin/env python
from distutils.core import setup

setup(name='CaseFOAM',
      description='Create and manipulate OpenFOAM cases',
      author='Joe Pearson',
      author_email='joe.pearson@dlr.de',
      url='https://github.com/DLR-RY/caseFOAM',
      packages=['casefoam', 'postprocessing'],
      package_dir={'casefoam': 'casefoam',
                   'postprocessing': 'postprocessing'},
      scripts=['scripts/foamState'],
      requires=['PyFoam', 'shutil', 'os', 'collections', 're',
                'sphinx_rtd_theme', 'argparse', 'datetime', 'subprocess'],
      )
