from setuptools import setup, find_packages

setup(
    name='sc_runner',
    version='0.1',
    description='Scenario runner for LB and API testing',
    url='',
    author='svasilenko',
    author_email='svasilenko@mirantis.com',
    license='Apache 2.0',
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'sc_runner = sc_runner.sc_runner:main'
        ]
    }
)
