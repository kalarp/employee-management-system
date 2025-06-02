# setup.py
"""
Setup script for Employee Management System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="employee-management-system",
    version="1.0.0",
    author="Your Company",
    author_email="info@yourcompany.com",
    description="A simple employee management system for small companies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourcompany/employee-management-system",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "tkcalendar>=1.6.1",
    ],
    entry_points={
        "console_scripts": [
            "employee-management=main:main",
        ],
    },
)