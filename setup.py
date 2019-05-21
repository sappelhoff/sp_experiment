"""Setup the package."""
import os
from setuptools import setup, find_packages

# get the version
version = None
with open(os.path.join('sp_experiment', '__init__.py'), 'r') as fid:
    for line in (line.strip() for line in fid):
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('\'')
            break
if version is None:
    raise RuntimeError('Could not determine version')

setup(name='sp_experiment',
      version=version,
      description='Implemetation of the Sampling Paradigm in PsychoPy',
      url='http://github.com/sappelhoff/sp_experiment',
      author='Stefan Appelhoff',
      author_email='stefan.appelhoff@mailbox.org',
      license='BSD 3-Clause License',
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'Operating System :: Microsoft :: Windows',
          'Intended Audience :: Science/Research',
      ],
      packages=find_packages(),
      zip_safe=False)
