from distutils.core import setup

version = '0.1'

setup(
    name='horensic',
    version=version,
    description='My Python library for developing digital forensic tools',
    author='Seonho Lee',
    author_email='horensic@gmail.com',
    url='https://github.com/horensic/horensic',
    # packages=[],
    scripts=['scripts/filehash',
             'scripts/jpgscan'],
    )
