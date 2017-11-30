from setuptools import setup, find_packages

setup(
    name='ab2json',
    version='0.1',
    description='AB output converter to JSON',
    url='',
    author='akasatkin',
    author_email='akasatkin@mirantis.com',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'ab2json = ab2json.ab2json:main'
        ]
    }
)
