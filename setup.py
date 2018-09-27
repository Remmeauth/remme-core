from setuptools import setup, find_packages

setup(
    name='remme',
    version='0.5.2-alpha',
    description='Distributed Public Key Infrastructure (PKI) protocol',
    author='REMME',
    url='https://remme.io',
    packages=find_packages(),
    package_data={
        'remme.rest_api': ['openapi.yml'],
        'remme.settings': ['default_config.toml']
    }
)
