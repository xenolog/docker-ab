from setuptools import setup, find_packages

setup(
    name='json2env',
    version='0.1',
    description='JSON to ENV converter',
    url='',
    author='svasilenko',
    author_email='svasilenko@mirantis.com',
    license='Apache 2.0',
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'json2env = json2env.json2env:main'
        ]
    }
)

