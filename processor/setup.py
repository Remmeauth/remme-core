from setuptools import setup, find_packages

data_files = []
setup(
    name='token',
    version='0.1',
    description='REMME Token cli',
    author='REMME Team',
    url='',
    packages=find_packages(),
    install_requires=[
    ],
    data_files=data_files,
    entry_points={
        'console_scripts': [
            'rem-token=processor.token.token_cli:main',
            'rem-crt=processor.certificate.certificate_cli:main'
        ]
    }
)
