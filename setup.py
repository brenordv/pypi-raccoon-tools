from setuptools import setup, find_packages

MAJOR = 1
MINOR = 0
BUILD = 0
VERSION = f"{MAJOR}.{MINOR}.{BUILD}"

setup(
    name="raccoontools",
    version=VERSION,
    description="A collection of tools, and helpers that I usually want for a handful of projects, so to avoid "
                "rewriting them every time, I decided to create this package.",
    long_description=open("readme.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Breno RdV",
    author_email="hello@raccoon.ninja",
    url="https://github.com/brenordv/pypi-raccoon-tools",
    project_urls={
        "Source": "https://github.com/brenordv/pypi-raccoon-tools",
        "Bug Tracker": "https://github.com/brenordv/pypi-raccoon-tools/issues",
        "Changelog": "https://github.com/brenordv/pypi-raccoon-tools/blob/master/changelog.md",
        "Author": "https://raccoon.ninja"
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "raccoon-simple-stopwatch==0.0.3",
        "simple-log-factory==0.0.1",
        "requests>=2.25.0",
        "pydantic>=1.8.2",
        "typing-extensions>=3.7.4.3"
    ],
    keywords=[
        "retry",
        "decorator",
        "benchmark",
        "logging",
        "requests",
        "json",
        "file operations",
        "serialization",
        "http",
        "utilities",
        "tools",
        "helpers",
        "python"
    ]
)
