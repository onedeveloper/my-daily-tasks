# CLAUDE.md

## Project Overview

A minimal Python CLI task manager designed specifically for daily standups. Tasks automatically roll forward until completed, uses SQLite for work session tracking, and generates accurate standup reports.

## Core Philosophy

**Keep it simple.** This tool has exactly 3 commands:
- `today` - show active tasks / add new task
- `today done <id>` - complete task
- `today standup` - generate standup report

## Tech Stack
- Python 3.12+
- Click (CLI framework)
- SQLite (database)
- Colorama/Tabulate (display)

## Project Structure
```
today/
├── cli.py          # CLI commands (3 total)
├── models.py       # Task, TaskStatus enums
├── database.py     # SQLite operations + work sessions
├── task_manager.py # Business logic
└── display.py      # Output formatting
```

## Database Schema

**tasks table:**
- id, description, status (pending/completed), date_created, date_completed

**work_sessions table:**
- id, task_id, work_date, created_at

## Key Features

1. **Work Session Tracking**: Every task interaction creates a work session entry
2. **Smart "Yesterday" Logic**: Finds your actual last work day (handles weekends/vacation)
3. **Minimal Interface**: No priorities, tags, or blocking - just tasks and completion
4. **Standup Reports**: Shows what you worked on your last work day + what you're working on today

## Installation
```bash
uv tool install .
```

## Usage
```bash
today                    # Show active tasks
today "fix the bug"      # Add task
today done 1            # Complete task 1
today standup           # Generate standup report
```

## Development Guidelines

1. **Resist feature creep** - Every new feature must justify its existence for daily standups
2. **Local-first** - All data in `~/.local/data/today.db`
3. **Test commands** - Always test basic workflow: add task, complete task, standup
4. **No complexity** - Max 200 chars for descriptions, simple status model

## Testing
```bash
uv run today "test task"
uv run today done 1
uv run today standup
```