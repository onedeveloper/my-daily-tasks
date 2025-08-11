# Installation Guide

## Quick Install Options

### Option 1: pip install from local directory (Recommended for Development)
```bash
# Clone the repository
git clone <repository-url>
cd claude-python-today

# Install in editable mode (changes to code reflected immediately)
pip install -e .

# Or install normally
pip install .
```

### Option 2: pip install directly from GitHub
```bash
pip install git+https://github.com/yourusername/today.git
```

### Option 3: pipx (Recommended for End Users)
```bash
# Install pipx if you haven't already
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install today-cli with pipx (isolated environment)
pipx install git+https://github.com/yourusername/today.git

# Or from local directory
pipx install .
```

### Option 4: Build and distribute wheel
```bash
# Build the package
python -m pip install build
python -m build

# This creates dist/ directory with:
# - today_cli-0.1.0-py3-none-any.whl
# - today_cli-0.1.0.tar.gz

# Users can install with:
pip install today_cli-0.1.0-py3-none-any.whl
```

### Option 5: Homebrew (macOS) - Future Enhancement
Create a Homebrew formula:
```ruby
class Today < Formula
  include Language::Python::Virtualenv

  desc "Simple CLI task manager for daily standups"
  homepage "https://github.com/yourusername/today"
  url "https://github.com/yourusername/today/archive/v0.1.0.tar.gz"
  sha256 "YOUR_SHA256_HERE"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end
end
```

## After Installation

Once installed via any method above, you can use the `today` command directly:

```bash
# Verify installation
today --version

# Get help
today --help

# Start using
today task "My first task"
today list
```

## Uninstall

```bash
# If installed with pip
pip uninstall today-cli

# If installed with pipx
pipx uninstall today-cli
```

## Distribution Best Practices

### For Personal Use
- Use `pip install -e .` for development
- Use `pipx install .` for isolated installation

### For Team Distribution
1. Push to private/public GitHub repo
2. Team members install with: `pip install git+https://github.com/org/repo.git`

### For Public Distribution
1. **PyPI** (Recommended)
   ```bash
   # Build the distribution
   python -m build
   
   # Upload to PyPI
   python -m twine upload dist/*
   
   # Users install with:
   pip install today-cli
   ```

2. **GitHub Releases**
   - Create releases with wheel files attached
   - Users download and `pip install today_cli-0.1.0-py3-none-any.whl`

3. **Standalone Executable** (Using PyInstaller)
   ```bash
   pip install pyinstaller
   pyinstaller --onefile --name today today/cli.py
   # Creates dist/today executable
   ```

## System-wide Installation

### Linux/macOS
```bash
# Install system-wide (requires sudo)
sudo pip install .

# Or copy to PATH after pipx install
pipx install .
sudo ln -s ~/.local/bin/today /usr/local/bin/today
```

### Windows
```powershell
# Install with pip
pip install .

# The 'today' command will be available if Python Scripts is in PATH
# Usually at: C:\Users\USERNAME\AppData\Local\Programs\Python\Python312\Scripts\
```

## Docker Distribution (Alternative)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install .
ENTRYPOINT ["today"]
```

## Recommended Approach

For most users, **pipx** is the best option because it:
- Creates an isolated environment
- Automatically adds to PATH
- Prevents dependency conflicts
- Easy to update/uninstall

```bash
pipx install git+https://github.com/yourusername/today.git
```