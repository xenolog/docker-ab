from setuptools import setup, find_packages

setup(
    name='gen_json_adder',
    version='0.1',
    description='Summarize test results in generic JSON format',
    url='',
    author='svasilenko',
    author_email='svasilenko@mirantis.com',
    license='Apache 2.0',
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'gen_json_adder = gen_json_adder.gen_json_adder:main'
        ]
    }
)

