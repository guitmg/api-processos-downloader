"""
Setup script for PJe TJMG Automation package.
"""

import os

from setuptools import find_packages, setup


# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [
            line.strip() for line in fh if line.strip() and not line.startswith("#")
        ]


setup(
    name="pje-tjmg-automation",
    version="1.0.0",
    author="PJe Automation Team",
    author_email="contact@example.com",
    description="Automação para o sistema PJe TJMG",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/user/pje-tjmg-automation",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pje-automation=pje_automation.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="pje, tjmg, automation, selenium, judicial, legal",
    project_urls={
        "Bug Reports": "https://github.com/user/pje-tjmg-automation/issues",
        "Source": "https://github.com/user/pje-tjmg-automation",
        "Documentation": "https://github.com/user/pje-tjmg-automation/wiki",
    },
)
