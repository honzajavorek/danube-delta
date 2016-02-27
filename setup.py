
import os
import sys
from codecs import open
from setuptools import setup, find_packages


version = '0.0.7'


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


if sys.argv[-1] == 'publish':
    import sh
    version_label = 'v{}'.format(version)
    sh.git.tag(a=version_label, m=version_label)
    sh.git.push('origin', 'master', '--tags')
    sys.exit()


setup(
    name='danube-delta',
    description='Honza Javorek\'s Pelican setup',
    long_description=long_description,
    version=version,
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
        'flake8',
        'markdown',
        'colorama',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'blog = danube_delta.cli:blog'
        ]
    },
    classifiers=[
        'Environment :: Console',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='pelican blog',
)
