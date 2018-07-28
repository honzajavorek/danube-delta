import sys
from setuptools import setup, find_packages

try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    message = "Unable to locate 'semantic_release', releasing won't work"
    print(message, file=sys.stderr)


version = '1.3.5'


install_requires = [
    'pelican',
    'ghp-import',
    'lxml',
    'pillow',
    'python-slugify',
    'click',
    'markdown',
    'colorama',
    'requests',
    'flake8',  # intentionally also here - used by 'blog lint'
]
tests_require = [
    'pytest-runner',
    'pytest',
    'pytest-cov',
    'coveralls',
    'flake8',
]
release_requires = [
    'python-semantic-release',
]


setup(
    name='danube-delta',
    version=version,
    description='Honza Javorek\'s Pelican setup',
    long_description=open('README.rst').read(),
    author='Honza Javorek',
    author_email='mail@honzajavorek.cz',
    url='http://github.com/honzajavorek/danube-delta',
    license=open('LICENSE').read(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'tests': tests_require,
        'release': release_requires,
    },
    entry_points={
        'console_scripts': [
            'blog = danube_delta.cli:blog'
        ]
    },
    classifiers=(
        'Environment :: Console',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
    ),
    keywords='pelican blog',
)
