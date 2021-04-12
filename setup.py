#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='animethemes-webm-verifier',
    version='1.1',
    author='AnimeThemes',
    author_email='admin@animethemes.moe',
    url='https://github.com/AnimeThemes/animethemes-webm-verifier',
    description='Verify WebM(s) Against AnimeThemes Encoding Standards',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)