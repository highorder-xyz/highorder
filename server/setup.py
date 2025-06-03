import os
import re

from setuptools import find_namespace_packages,  setup

install_requires = [
    'callpy>=0.4.0',
    'aiobotocore',
    'asyncpg',
    'basepy>=0.5',
    'httpx',
    'phonenumbers',
    'arrow',
    'dataclass_factory',
    'likepy>=0.3.0',
    'postmodel>=0.3.0',
    'dominate==2.9.1',
    'html5lib==1.1',
    'aiofiles',
    'rich'
]
# pip install -e '.[test]'
test_requires = [
    'asynctest',
    'pytest',
    'pytest-asyncio',
    'pytest-cov',
    'pytest-mock'
]

here = os.path.dirname(os.path.abspath(__file__))
with open(
        os.path.join(here, 'highorder/__init__.py'), 'r', encoding='utf8'
) as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='highorder',
    version=version,
    license='AGPL',
    packages=find_namespace_packages(include=['highorder', 'highorder.*']),
    include_package_data=False,
    zip_safe=True,
    install_requires=install_requires,
    platforms='any',
    extras_require={
        'test': test_requires,
    },
    entry_points={
    }
)
