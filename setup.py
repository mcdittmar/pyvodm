from setuptools import setup, find_packages
from os import environ

name = 'pyvodm'

setup(name=name,
      version='1.0.0',
      description='Package of utility classes for use in VO related tools',
      author='Smithsonian Astrophysical Observatory / Chandra X-Ray Center',
      author_email='mdittmar@cfa.harvard.edu',
      classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: VO Developers',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # These classifiers are *not* checked by 'pip install'. See instead
        # 'python_requires' below.
        'Programming Language :: Python :: 3.5',
      ],

      #py_modules=['__init__'],
      #packages=['.'],
      packages=find_packages(exclude=['resources', 'tests', 'voefg']),
      )
