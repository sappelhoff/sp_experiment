"""Setup the package."""
import os
from setuptools import setup, find_packages

# get the version
version = None
with open(os.path.join('sp_psychopy', '__init__.py'), 'r') as fid:
    for line in (line.strip() for line in fid):
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('\'')
            break
if version is None:
    raise RuntimeError('Could not determine version')

setup(name='sp_psychopy',
      version=version,
      description='Implemetation of the Sampling Paradigm in PsychoPy',
      url='http://github.com/sappelhoff/sp_psychopy',
      author='Stefan Appelhoff',
      author_email='stefan.appelhoff@mailbox.org',
      license='BSD 3-Clause License',
      packages=find_packages(),
      zip_safe=False)
