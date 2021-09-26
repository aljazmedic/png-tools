from setuptools import setup, find_packages
import pathlib, pkg_resources

with pathlib.Path('requirements.txt').open("r",encoding="utf-8") as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]

setup(name='inspect_png',
      version='0.1',
      packages=find_packages(),
      zip_safe=False,
      entry_points = {
          'console_scripts': ['inspect_png=inspect_png.main:main'],
      },
      install_requires=install_requires
)
