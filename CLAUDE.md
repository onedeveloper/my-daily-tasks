# CLAUDE.md

## Project Overview

A Python CLI task manager for daily standups and productivity tracking. Tasks automatically roll forward if incomplete, uses local SQLite storage, and generates formatted standup reports.

## Tech Stack
- Python 3.12+, Click (CLI), SQLite (database), Colorama/Tabulate (display)
- Virtual environment: `source .venv/bin/activate`
- Install: `pip install -e .`

## Project Structure
```
today/
├── cli.py          # CLI commands entry point
├── models.py       # Task, TaskStatus, Priority enums
├── database.py     # SQLite operations
├── task_manager.py # Business logic
└── display.py      # Output formatting
```

## Key Commands
```bash
# Core operations
today                      # Show tasks (default behavior)
today task "description"    # Add task
today list                  # Show tasks (explicit command)
today done <id>            # Complete task
today working <id>         # Mark as in-progress

# Organization
today priority <id> high   # Set priority (high/medium/low)
today tag <id> bug        # Add tag
today block <id> "reason" # Block with reason
today unblock <id>        # Unblock task

# Reports
today standup             # Daily standup report
today yesterday           # Yesterday's completed tasks
today week               # Weekly summary
today stats              # Productivity metrics
today summary [days]     # N-day summary (default: 7)
today archive [days]     # Archive old tasks (default: 30)

# Filtering
today list --priority high
today list --tag bug
today list --completed
today list --blocked
```

## Database Schema
- SQLite database at `~/.local/data/today.db`
- Single `tasks` table with columns:
  - id (PRIMARY KEY), description, status, priority
  - tags (JSON), dates (created/started/completed/due)
  - blocker_reason, archived (boolean)

## Data Models
- **TaskStatus**: PENDING, WORKING, BLOCKED, COMPLETED
- **Priority**: HIGH, MEDIUM, LOW
- **Tags**: Stored as JSON array, lowercase, alphanumeric + hyphen/underscore

## Development Guidelines

1. **Keep it simple** - Avoid feature creep, this is a focused CLI tool
2. **Local-first** - All data in `~/.local/data/today.db`, no cloud dependencies
3. **Test commands** - Always test with: `today task "test"`, `today list`, `today done 1`
4. **No build system** - Pure Python, no compilation needed
5. **Validation** - Max 200 chars for descriptions, 20 chars for tags
6. **Error handling** - Never crash on bad input, show helpful error messages

## Testing
```bash
source .venv/bin/activate
pip install -e .
today --version  # Should show 0.1.0

# Quick functionality test
today task "Test task"
today list
today done 1
```

## Distribution
- Install: `pip install -e .` (development) or `pipx install .` (users)
- Uninstall: `pip uninstall today-cli`
- Entry point: `today` command via console_scripts

## Important Files
- `README.md` - User documentation and installation guide
- `setup.py` & `pyproject.toml` - Package configuration
- `requirements.txt` - Python dependencies

## Common Tasks

### Add new command
1. Add @cli.command() function in cli.py
2. Add business logic in task_manager.py
3. Add display formatter in display.py if needed

### Modify database
1. Update _create_tables() in database.py
2. Update Task model in models.py
3. Update _task_from_row() in database.py