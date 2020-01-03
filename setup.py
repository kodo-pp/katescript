from setuptools import setup


setup(
    name = 'katescript',
    version = '1.0.1',
    license = 'CC0',
    description = 'A simple scripting language',
    zip_safe = False,
    packages = ['kates'],
    tests_require = ['pytest'],
    setup_requires = ['pytest-runner'],
    package_data = {'kates': ['py.typed']},
)
