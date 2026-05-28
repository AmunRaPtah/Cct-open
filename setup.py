from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cct-open",
    version="0.1.0-dev",
    author="Eniola Olutogun",
    description=(
        "Open source computational framework for addiction liability "
        "prediction in CNS drug discovery and BCI safety"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Amunraptah/cct-open",
    project_urls={
        "Theoretical Framework": "https://doi.org/10.5281/zenodo.20427785",
        "Bug Tracker": "https://github.com/Amunraptah/cct-open/issues",
    },
    packages=find_packages(exclude=["tests*", "docs*"]),
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.24",
        "scipy>=1.10",
        "pandas>=2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    keywords=[
        "computational pharmacology",
        "addiction liability",
        "CNS drug discovery",
        "BCI safety",
        "reward memory",
        "consolidation control theory",
    ],
)
