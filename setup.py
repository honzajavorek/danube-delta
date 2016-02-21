
import os
from codecs import open
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='danube_delta',
    description='Honza Javorek\'s Pelican setup',
    long_description=long_description,
    version='0.0.1',
    url='http://github.com/honzajavorek/danube-delta',
    author='Honza Javorek',
    author_email='mail@honzajavorek.cz',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'pelican',
        'ghp-import',
        'lxml',
        'pillow',
        'python-slugify',
        'click',
        'sh',
    ],
    extras_require={  # pip install -e .[dev,test]
        'dev': ['flake8'],
        'test': ['flake8'],
    },
    entry_points='''
        [console_scripts]
        blog=danube_delta.cli:main
    ''',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='pelican blog',
)
