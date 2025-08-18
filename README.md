# Today CLI

A minimal task manager designed specifically for daily standups. No bloat, just the essentials.

## Features

- **3 commands total**: `today`, `today done <id>`, `today standup`
- **Smart work tracking**: Knows your actual last work day (handles weekends/vacation)
- **Automatic rollover**: Incomplete tasks automatically appear in your task list
- **Local SQLite storage**: All data stays on your machine

## Installation

### With uv (recommended)
```bash
git clone <this-repo>
cd my-daily-tasks
uv tool install .
```

### With pip
```bash
git clone <this-repo>
cd my-daily-tasks
pip install .
```

## Usage

### Daily Workflow
```bash
# Start your day - see what's pending
today

# Add new tasks
today "fix authentication bug"
today "review PR #123"

# Complete tasks as you finish them
today done 1
today done 2

# Generate standup report
today standup
```

### Example Output

**Task List:**
```
  ID  Status    Description              Created
----  --------  -----------------------  ----------------
   3  ⚡         fix authentication bug   2025-08-18 09:15
   4  ⚡         review PR #123           2025-08-18 10:30
```

**Standup Report:**
```
═══ STANDUP REPORT ═══

▶ YESTERDAY
  ✓ implement user login (completed)
  • refactor database layer (worked on)

▶ TODAY
  ⚡ fix authentication bug (in progress)
  ⚡ review PR #123 (in progress)
```

## Commands

| Command | Description |
|---------|-------------|
| `today` | Show active tasks, or add task if description provided |
| `today done <id>` | Mark task as completed |
| `today standup` | Generate standup report showing yesterday's work + today's tasks |

## Data Storage

Tasks are stored locally in `~/.local/data/today.db`. No cloud sync, no accounts, no tracking.

## Why Another Task Manager?

Most task managers are bloated with features you don't need for daily standups:
- ❌ Priority levels
- ❌ Tags and categories  
- ❌ Due dates and reminders
- ❌ Projects and contexts
- ❌ Blocking and dependencies

This tool focuses on one thing: **helping you remember what you worked on for standups**.

## License

MIT