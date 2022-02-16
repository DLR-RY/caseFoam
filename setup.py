#!/usr/bin/env python

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext
from setuptools import setup, find_packages

def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()
setup(
    name='casefoam',
    version='0.1.0',
    license='GPLv3',
    description='Create and manipulate OpenFOAM cases',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='Joe Pearson and Henning Scheufler',
    author_email='Henning.Scheufler@dlr.de',
    url='https://github.com/DLR-RY/caseFoam',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    scripts=['bin/foamState'],
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering'
    ],
    project_urls={
        'Documentation': 'https://casefoam.readthedocs.io/en/latest/',
        # 'Changelog': 'https://casefoam.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/DLR-RY/caseFoam/issues',
    },
    keywords=[
        'cfd', 'openfoam', 'postProcessing', 'automation'
    ],
    python_requires='>=3.6',
    install_requires=[
        'pyfoam>=0.6.7','pandas>=0.23.0'
    ],
    extras_require={
          'dev': ['pytest>=6.2.3','sphinx_rtd_theme','numpydoc','sphinx','ipython'],
          'plot': ['seaborn>=0.8']
    }
)
