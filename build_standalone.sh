#!/bin/bash

# Build standalone executable using PyInstaller
# This creates a single binary file that includes Python and all dependencies

echo "Building standalone executable..."

# Install PyInstaller if not already installed
pip install pyinstaller

# Create the standalone executable
pyinstaller \
    --onefile \
    --name today \
    --add-data "today/*.py:today" \
    --hidden-import click \
    --hidden-import colorama \
    --hidden-import tabulate \
    --hidden-import dateutil \
    --distpath ./dist \
    --workpath ./build \
    --specpath ./build \
    today/cli.py

echo "Build complete! Executable is at ./dist/today"
echo "You can copy ./dist/today to /usr/local/bin/ for system-wide access:"
echo "  sudo cp ./dist/today /usr/local/bin/"