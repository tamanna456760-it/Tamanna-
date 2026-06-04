#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup configuration for Tamanna AI Package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="tamanna-ai",
    version="2.0.0",
    description="Autonomous Code Analysis, Fixing, and Synchronization System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tamanna AI",
    author_email="tamanna@example.com",
    url="https://github.com/tamanna456760-it/Tamanna-",
    project_urls={
        "Bug Tracker": "https://github.com/tamanna456760-it/Tamanna-/issues",
        "Documentation": "https://github.com/tamanna456760-it/Tamanna-/wiki",
        "Source Code": "https://github.com/tamanna456760-it/Tamanna-"
    },
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "psutil>=5.9.0",
        "requests>=2.31.0",
        "GitPython>=3.1.40",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "pylint>=3.0.0",
            "mypy>=1.7.0",
        ],
        "docs": [
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=2.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "tamanna=src.core.main:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Monitoring",
    ],
    keywords="ai automation code-analysis git-sync monitoring",
)
