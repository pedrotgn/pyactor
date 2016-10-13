from setuptools import setup


setup(
    name='pyactor',
    version='0.9',
    author='Pedro Garcia Lopez & Daniel Barcelona Pons',
    author_email='pedro.garcia@urv.cat, daniel.barcelona@urv.cat',
    packages=['pyactor', 'pyactor.green_thread', 'pyactor.thread'],
    url='https://github.com/pedrotgn/pyactor',
    license='LICENSE.txt',
    description='Python Actor Middleware',
    long_description=open('README.md').read(),
)
