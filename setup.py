"""Setup script for agenix."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Dependencies
requirements = [
    "openai>=1.12.0",
    "anthropic>=0.18.0",
    "rich>=13.7.0",
    "pyyaml>=6.0",
    "prompt_toolkit>=3.0.0",  # Better terminal input with unicode support
]

dev_requirements = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
]

docs_requirements = [
    "sphinx>=8.0.0",
    "sphinx-rtd-theme>=3.0.0",
    "myst-parser>=5.0.0",
]

setup(
    name="agenix",
    version="0.0.1",
    author="ZHANG Zhi",
    author_email="tczhangzhi@gmail.com",
    description="A lightweight AI coding agent with file operations and shell execution capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tczhangzhi/agenix",
    project_urls={
        "Bug Tracker": "https://github.com/tczhangzhi/agenix/issues",
        "Source Code": "https://github.com/tczhangzhi/agenix",
        "Changelog": "https://github.com/tczhangzhi/agenix/blob/main/CHANGELOG.md",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "docs": docs_requirements,
    },
    entry_points={
        "console_scripts": [
            "agenix=agenix.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="ai agent coding llm openai anthropic claude automation cli assistant gpt-4 agenix",
)
