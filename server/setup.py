import os
import re

from setuptools import find_namespace_packages,  setup

install_requires = [
    'callpy>=0.4.0dev',
    'aiobotocore',
    'asyncpg',
    'basepy',
    'httpx',
    'phonenumbers',
    'dataclass_factory',
    'likepy',
    'postmodel',
    'aiofiles',
    'redis',
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
