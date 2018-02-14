from setuptools import setup, find_packages

setup(
    name='pyactor',
    version='1.4.0',
    author='Pedro Garcia Lopez & Daniel Barcelona Pons',
    author_email='pedro.garcia@urv.cat, daniel.barcelona@urv.cat',
    packages=find_packages(),
    url='https://github.com/pedrotgn/pyactor',
    license='GNU',
    description='The minimalistic Python Actor middleware',
    long_description=open('README.rst').read(),
    install_requires=['gevent==1.2.2'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',

        'License :: OSI Approved :: GNU Lesser General Public' +
        ' License v3 (LGPLv3)',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
