from setuptools import setup, find_packages

data_files = []
setup(
    name='remme',
    version='0.1',
    description='REMME',
    author='REMME',
    url='',
    packages=find_packages(),
    install_requires=[
    ],
    data_files=data_files,
    entry_points={
        'console_scripts': [
            'rem-token=remme.token.token_cli:main',
            'rem-crt=remme.certificate.certificate_cli:main'
        ]
    }
)
