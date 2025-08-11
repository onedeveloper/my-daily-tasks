from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="today-cli",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple CLI task manager for daily standups",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/today",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=[
        "click>=8.1.7",
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
        "python-dateutil>=2.9.0",
    ],
    entry_points={
        "console_scripts": [
            "today=today.cli:main",
        ],
    },
)