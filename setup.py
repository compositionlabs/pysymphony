from setuptools import setup, find_packages

setup(
    name='pysymphony',
    version='0.2.0',
    description='A Python client for Symphony',
    author='Chinmay Shrivastava',
    author_email='cshrivastava99@gmail.com',
    url='https://github.com/compositionlabs/pysymphony',
    packages=find_packages(),
    install_requires=[
        'certifi==2024.8.30',
        'charset-normalizer==3.3.2',
        'idna==3.10',
        'requests==2.32.3',
        'urllib3==2.2.3',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
