import os

import setuptools

version = {}
exec(open(os.path.join('autotrade', 'version.py')).read(), version)
test_require = ['nose', 'coverage', 'pylint']

setuptools.setup(
    name='autotrade',
    version=version['__version__'],
    description='Automated trading framework.',
    packages=setuptools.find_packages(),
    install_require=[],
    test_suite='nose.collector',
    test_require=test_require,
    extras_require={'test': test_require}
)
