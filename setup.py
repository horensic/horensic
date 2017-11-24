from setuptools import setup, find_packages

version = '0.1'

install_requires = []

setup_requires = []

setup(
    name='horensic',
    version=version,
    description='My Python library for developing digital forensic tools',
    author='Seonho Lee',
    author_email='horensic@gmail.com',
    url='https://github.com/horensic/horensic',
    packages=find_packages(),
    install_requires=install_requires,
    setup_requires=setup_requires,
    scripts=[
        'scripts/filehash',
        'scripts/jpgscan'
    ],
)
