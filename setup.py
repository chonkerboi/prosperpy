import os

import setuptools

version = {}
exec(open(os.path.join('prosperpy', 'version.py')).read(), version)
tests_require = ['nose', 'coverage', 'pylint']
install_require = ['websockets', 'requests']

setuptools.setup(
    name='prosperpy',
    version=version['__version__'],
    description='Automated trading framework.',
    python_requires='>=3.5',
    packages=setuptools.find_packages(),
    install_require=install_require,
    test_suite='nose.collector',
    tests_require=tests_require,
    extras_require={'test': tests_require, 'all': install_require + tests_require}
)
