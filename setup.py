from setuptools import setup


setup(
    name='pyactor',
    version='0.1',
    author='Pedro Garcia Lopez & Daniel Barcelona Pons',
    author_email='pedro.garcia@urv.cat',
    packages=['pyactor', 'pyactor.green_thread', 'pyactor.thread'],
    url='https://github.com/pedrotgn/pyactor',
    license='LICENSE.txt',
    description='Python Actor Middleware',
    long_description=open('README.md').read(),
)
