from setuptools import setup, find_packages

setup(name='inspect_png',
      version='0.1',
      packages=find_packages(),
      zip_safe=False,
      entry_points = {
          'console_scripts': ['inspect_png=inspect_png:main'],
      }
)
