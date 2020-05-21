from distutils.core import setup

setup(
    name='Roku Direct Publisher JSON Generator',
    author='Timothy Palko',
    author_email='tim@palkosoftware.com',
    version='0.1',
    scripts=['scripts/rodipugen.py'],
    license='GPLv3',
    long_description=open('README').read(),
    url='http://palkosoftware.ddns.net/software/rodipugen',
)
