#!/usr/bin/env python

from distutils.core import setup

setup(name='CaseFOAM',
      version="2.0",
      description='Create and manipulate OpenFoam cases',
      author='Joe Pearson',
      author_email='joe.pearson@dlr.de',
      url='https://git.gnc.dlr.de/pear_jo/CaseFOAM',
      packages=['casefoam', 'postprocessing'],
      package_dir={'casefoam': 'casefoam',
                   'postprocessing': 'postprocessing'},
      scripts=['scripts/foamState'],
      requires=['PyFoam', 'shutil', 'os', 'collections', 're',
                'sphinx_rtd_theme', 'argparse', 'datetime', 'subprocess'],
      )
