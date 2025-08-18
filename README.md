# today - CLI Task Manager

A simple, local-first CLI task manager designed for daily standups and productivity tracking. Keep track of what you're working on, generate standup reports, and never lose track of tasks with automatic rolling forward.

## Features

- 📝 **Simple task management** - Add, complete, and track tasks from your terminal
- 🚀 **Standup integration** - Generate formatted reports for daily standups
- 🔄 **Rolling tasks** - Incomplete tasks automatically carry forward to the next day
- 🏷️ **Organization** - Priority levels, tags, and status tracking
- 💾 **Local SQLite storage** - All data stays on your machine, no cloud dependencies
- 🎨 **Colorized output** - Clean, readable terminal interface
- 📊 **Productivity stats** - Track completion rates and task metrics

## Installation

### Prerequisites

- Python 3.12 or higher
- pip (Python package installer)

### Quick Install

#### Option 1: Using pipx (Recommended)

```bash
# Install pipx if you don't have it
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install today
pipx install git+https://github.com/yourusername/today.git
```

#### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/today.git
cd today

# Install the package
pip install .

# Or for development (editable install)
pip install -e .
```

#### Option 3: Direct from GitHub

```bash
pip install git+https://github.com/yourusername/today.git
```

### Verify Installation

```bash
today --version
# Output: today, version 0.1.0
```

## Usage

### Basic Commands

```bash
# List all tasks (default behavior when no command provided)
today

# Add a new task
today task "Review pull request #123"

# List all tasks (explicit command)
today list

# Mark task as currently working
today working 1

# Complete a task
today done 1

# Generate standup report
today standup
```

### Task Management

```bash
# Set task priority (high, medium, low)
today priority 2 high

# Add tags to tasks
today tag 3 bug
today tag 3 frontend

# Block a task with reason
today block 4 "Waiting for API access"

# Unblock a task
today unblock 4
```

### Filtering and Views

```bash
# List tasks with filters
today list --priority high
today list --tag bug
today list --completed
today list --pending
today list --working
today list --blocked

# View yesterday's completed tasks
today yesterday

# Show summary of past N days (default: 7)
today summary 14

# Weekly report
today week

# Productivity statistics
today stats
```

### Archive Management

```bash
# Archive completed tasks older than N days (default: 30)
today archive 60
```

## Examples

### Daily Workflow

```bash
# Start your morning - see what's on your plate
$ today list
  ID  Status    Priority    Description                     Tags    Created
----  --------  ----------  ------------------------------  ------  ----------------
   5  ○         HIGH        Fix critical production bug     bug     2025-01-11 09:00
   3  ⚡        MEDIUM      Implement user authentication  auth    2025-01-10 14:30
   2  ○         MEDIUM      Write unit tests                test    2025-01-10 10:15
   4  ⚠         LOW         Update documentation            docs    2025-01-09 16:45

# Start working on the high priority bug
$ today working 5
⚡ Now working on task [5]: Fix critical production bug

# Add a new task that came up
$ today task "Review Jane's PR for feature X"
✓ Task [6] added: Review Jane's PR for feature X

# Complete the bug fix
$ today done 5
✓ Task [5] completed: Fix critical production bug

# Generate standup report
$ today standup

═══ STANDUP REPORT ═══

▶ YESTERDAY
  ✓ Setup development environment
  ✓ Attend architecture review meeting

▶ TODAY
  ⚡ Implement user authentication (in progress)
  • Review Jane's PR for feature X (high priority)

▶ BLOCKERS
  ⚠ Update documentation: Waiting for technical writer review
```

### Weekly Review

```bash
$ today week

═══ WEEKLY REPORT ═══

Completed 23 task(s) this week:

HIGH PRIORITY (5 tasks)
  ✓ Fix critical production bug
  ✓ Resolve customer data issue
  ✓ Emergency deploy hotfix
  ... and 2 more

MEDIUM PRIORITY (15 tasks)
  ✓ Implement user authentication
  ✓ Add input validation
  ✓ Setup CI/CD pipeline
  ... and 12 more

LOW PRIORITY (3 tasks)
  ✓ Update README
  ✓ Clean up old branches
  ✓ Organize team documentation
```

## Data Storage

Tasks are stored in a local SQLite database at `~/.local/data/today.db`. This ensures:
- Fast performance
- Data persistence
- No network dependencies
- Easy backup (just copy the `.db` file)

### Backup Your Data

```bash
# Backup
cp ~/.local/data/today.db ~/today-backup-$(date +%Y%m%d).db

# Restore
cp ~/today-backup-20250111.db ~/.local/data/today.db
```

## Uninstall

### If installed with pipx
```bash
pipx uninstall today-cli
```

### If installed with pip
```bash
pip uninstall today-cli
```

### Clean up data (optional)
```bash
rm -rf ~/.local/data/today.db
```

## Troubleshooting

### Command not found

If `today` command is not found after installation:

1. **Check if it's installed:**
   ```bash
   pip list | grep today-cli
   ```

2. **Find where it's installed:**
   ```bash
   which today
   # or
   pip show -f today-cli | grep today
   ```

3. **Add to PATH (if needed):**
   ```bash
   # Add Python scripts to PATH
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Permission denied

If you get permission errors:
```bash
# Install in user space
pip install --user .

# Or use pipx (recommended)
pipx install .
```

### Database issues

If tasks aren't saving or loading:

1. **Check database location:**
   ```bash
   ls -la ~/.local/data/today.db
   ```

2. **Reset database (WARNING: loses all data):**
   ```bash
   rm ~/.local/data/today.db
   # The app will create a new database on next run
   ```

3. **Check permissions:**
   ```bash
   chmod 644 ~/.local/data/today.db
   ```

### Import errors

If you get Python import errors:

1. **Verify Python version:**
   ```bash
   python --version  # Should be 3.12+
   ```

2. **Reinstall dependencies:**
   ```bash
   pip install --upgrade click colorama tabulate python-dateutil
   ```

3. **Reinstall the package:**
   ```bash
   pip uninstall today-cli
   pip install .
   ```

### Colorized output not working

If colors aren't showing in terminal:

1. **Windows users:** Install Windows Terminal or use PowerShell
2. **Force colors:**
   ```bash
   export FORCE_COLOR=1
   today list
   ```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/today.git
cd today

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode
pip install -e .

# Install dev dependencies
pip install pytest black flake8
```

### Run Tests

```bash
pytest tests/
```

### Project Structure

```
today/
├── today/
│   ├── __init__.py
│   ├── cli.py          # CLI commands and interface
│   ├── models.py       # Data models (Task, Status, Priority)
│   ├── database.py     # SQLite database operations
│   ├── task_manager.py # Business logic
│   └── display.py      # Output formatting
├── setup.py            # Package configuration
├── pyproject.toml      # Modern Python packaging
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the simplicity of command-line task management
- Built with Python's excellent Click library for CLI interfaces
- Colorized output powered by Colorama
- Table formatting by Tabulate

## Support

For issues, questions, or suggestions, please open an issue on [GitHub](https://github.com/yourusername/today/issues).