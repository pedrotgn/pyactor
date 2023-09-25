from setuptools import setup, find_packages
from pyactor import __version__

setup(
    name='pyactor',
    version=__version__,
    author='Pedro Garcia Lopez & Daniel Barcelona Pons',
    author_email='pedro.garcia@urv.cat, daniel.barcelona@urv.cat',
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    url='https://github.com/pedrotgn/pyactor',
    license='GNU',
    description='The minimalistic Python Actor middleware',
    long_description=open('README.rst').read(),
    install_requires=['gevent==23.9.1'],
    # gevent 1.4.0 does not work with python 3.8
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',

        'License :: OSI Approved :: GNU Lesser General Public' +
        ' License v3 (LGPLv3)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
)
