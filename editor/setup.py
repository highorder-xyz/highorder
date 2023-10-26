from setuptools import setup, find_packages
from functools import reduce
import os, re

install_requires = [
    'basepy',
    'httpx',
    'wavegui',
    'typer',
    'dataclasses-json',
    'dictdiffer',
    'rich'
]
here = os.path.dirname(os.path.abspath(__file__))
with open(
        os.path.join(here, 'highorder_editor/__init__.py'), 'r', encoding='utf8'
) as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='highorder_editor',
    version=version,
    install_requires=install_requires,
    packages=find_packages(include=["highorder_editor"]),
    include_package_data=True,
    zip_safe=False,
    license='AGPL',
    entry_points={
    },
)
