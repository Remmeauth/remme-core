from setuptools import setup, find_packages

data_files = []
setup(
    name='remme',
    version='0.2.0-alpha',
    description='Distributed Public Key Infrastructure (PKI) protocol',
    author='REMME',
    url='https://remme.io',
    packages=find_packages(),
    install_requires=[
        'colorlog',
        'cryptography',
        'sawtooth-sdk',
        'sawtooth-signing'
    ],
    data_files=data_files,
    entry_points={
        'console_scripts': [
            'rem-token=remme.token.token_cli:main',
            'rem-crt=remme.certificate.certificate_cli:main'
        ]
    }
)
