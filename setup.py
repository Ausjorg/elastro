import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="elastro",
    version="0.1.0",
    author="Austin Jorgensen",
    description="A Python module for managing Elasticsearch operations within a pipeline process",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Repository": "https://github.com/Fremen-Labs/elastro",
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database :: Database API",
    ],
    python_requires=">=3.8",
    install_requires=[
        "elasticsearch==8.18.0",
        "click>=8.0.0",
        "python-dotenv>=0.19.0",
        "pydantic==2.11.3",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "elastic-cli=elastro.cli.cli:main",
        ],
    },
) 