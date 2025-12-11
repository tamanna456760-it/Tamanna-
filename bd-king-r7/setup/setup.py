# File: setup.py
# Purpose: Package installer for Tamanna system (example)
# Usage: python setup.py install OR pip install .

from setuptools import find_packages, setup

setup(
    name="tamanna-system",  # Package name
    version="1.0.0",  # Semantic version
    description="Tamanna sovereign system core package",
    long_description=open("README.md").read(),  # Optional: project README
    long_description_content_type="text/markdown",
    author="HM INSAN ALI",  # Your name
    author_email="tamanna456760@gmail.com",  # Replace with your email
    url="https://github.com/yourrepo/tamanna-system",  # Project URL
    packages=find_packages(),  # Auto-discover Python packages
    include_package_data=True,  # Include non-code files (MANIFEST.in)
    install_requires=[  # Dependencies
        "requests>=2.25.0",
        "numpy>=1.21.0",
    ],
    classifiers=[  # Metadata for PyPI
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # Minimum Python version
    entry_points={  # Optional: CLI commands
        "console_scripts": [
            "tamanna=tamanna.cli:main",  # e.g. run `tamanna` in terminal
        ],
    },
)
