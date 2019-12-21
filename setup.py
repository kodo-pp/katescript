from setuptools import setup


setup(
    name = 'katescript',
    version = '1.0.0',
    license = 'CC0',
    description = 'A simple scripting language',
    packages = ['kates'],
    tests_require = ['pytest'],
    setup_requires = ['pytest-runner'],
)
