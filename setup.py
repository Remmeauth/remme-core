from setuptools import setup, find_packages

setup(
    name='remme',
    version='0.3.1-alpha',
    description='Distributed Public Key Infrastructure (PKI) protocol',
    author='REMME',
    url='https://remme.io',
    packages=find_packages(),
    install_requires=[
        'requests',
        'protobuf',
        'colorlog',
        'sawtooth-sdk',
        'sawtooth-signing',
        'cryptography',
        'connexion'
    ],
    package_data={'remme.rest_api': ['openapi.yml']}
)
