from typing import List
from datetime import datetime
from colorama import Fore, Style, init
from tabulate import tabulate

from .models import Task, TaskStatus, Priority

init(autoreset=True)


def format_task_added(task_id: int, description: str) -> str:
    return f"{Fore.GREEN}✓{Style.RESET_ALL} Task [{task_id}] added: {description}"


def format_task_completed(task_id: int, description: str) -> str:
    return f"{Fore.GREEN}✓{Style.RESET_ALL} Task [{task_id}] completed: {description}"


def format_task_working(task_id: int, description: str) -> str:
    return f"{Fore.YELLOW}⚡{Style.RESET_ALL} Now working on task [{task_id}]: {description}"


def format_task_not_found(task_id: int) -> str:
    return f"{Fore.RED}✗{Style.RESET_ALL} Task [{task_id}] not found"


def format_archive_result(count: int, days: int) -> str:
    if count > 0:
        return f"{Fore.GREEN}✓{Style.RESET_ALL} Archived {count} task(s) older than {days} days"
    else:
        return f"{Fore.YELLOW}✓{Style.RESET_ALL} No tasks to archive (older than {days} days)"


def _get_status_icon(status: TaskStatus) -> str:
    icons = {
        TaskStatus.PENDING: "○",
        TaskStatus.WORKING: f"{Fore.YELLOW}⚡{Style.RESET_ALL}",
        TaskStatus.BLOCKED: f"{Fore.RED}⚠{Style.RESET_ALL}",
        TaskStatus.COMPLETED: f"{Fore.GREEN}✓{Style.RESET_ALL}"
    }
    return icons.get(status, "?")


def _get_priority_color(priority: Priority) -> str:
    colors = {
        Priority.HIGH: Fore.RED,
        Priority.MEDIUM: Fore.YELLOW,
        Priority.LOW: Fore.CYAN
    }
    return colors.get(priority, "")


def format_task_list(tasks: List[Task]) -> str:
    if not tasks:
        return f"{Fore.YELLOW}No tasks found{Style.RESET_ALL}"
    
    headers = ["ID", "Status", "Priority", "Description", "Tags", "Created"]
    rows = []
    
    for task in tasks:
        status_icon = _get_status_icon(task.status)
        priority_color = _get_priority_color(task.priority)
        priority_text = f"{priority_color}{task.priority.value.upper()}{Style.RESET_ALL}"
        
        description = task.description
        if task.status == TaskStatus.BLOCKED and task.blocker_reason:
            description += f" {Fore.RED}[BLOCKED: {task.blocker_reason}]{Style.RESET_ALL}"
        
        tags = ", ".join(task.tags) if task.tags else ""
        created = task.date_created.strftime("%Y-%m-%d %H:%M")
        
        rows.append([task.id, status_icon, priority_text, description, tags, created])
    
    return tabulate(rows, headers=headers, tablefmt="simple")


def format_standup_report(
    yesterday_completed: List[Task],
    today_working: List[Task],
    today_priority: List[Task],
    blocked: List[Task],
    rolling: List[Task]
) -> str:
    report = []
    report.append(f"\n{Fore.CYAN}═══ STANDUP REPORT ═══{Style.RESET_ALL}\n")
    
    # Yesterday section
    report.append(f"\n{Fore.GREEN}▶ YESTERDAY{Style.RESET_ALL}")
    if yesterday_completed:
        for task in yesterday_completed:
            report.append(f"  ✓ {task.description}")
    else:
        report.append(f"  {Fore.YELLOW}No tasks completed yesterday{Style.RESET_ALL}")
    
    # Today section
    report.append(f"\n{Fore.BLUE}▶ TODAY{Style.RESET_ALL}")
    today_tasks = today_working + today_priority
    if today_tasks:
        for task in today_working:
            report.append(f"  ⚡ {task.description} (in progress)")
        for task in today_priority:
            report.append(f"  • {task.description} (high priority)")
    else:
        report.append(f"  {Fore.YELLOW}No tasks in progress{Style.RESET_ALL}")
    
    # Rolling tasks
    if rolling:
        report.append(f"\n{Fore.YELLOW}▶ ROLLING FORWARD{Style.RESET_ALL}")
        for task in rolling[:5]:  # Show max 5
            report.append(f"  ↻ {task.description}")
        if len(rolling) > 5:
            report.append(f"  ... and {len(rolling) - 5} more")
    
    # Blockers section
    report.append(f"\n{Fore.RED}▶ BLOCKERS{Style.RESET_ALL}")
    if blocked:
        for task in blocked:
            report.append(f"  ⚠ {task.description}: {task.blocker_reason}")
    else:
        report.append(f"  {Fore.GREEN}No blockers{Style.RESET_ALL}")
    
    report.append("")
    return "\n".join(report)


def format_yesterday_tasks(tasks: List[Task]) -> str:
    if not tasks:
        return f"{Fore.YELLOW}No tasks completed yesterday{Style.RESET_ALL}\n"
    
    report = [f"\n{Fore.GREEN}═══ YESTERDAY'S COMPLETED TASKS ═══{Style.RESET_ALL}\n"]
    for task in tasks:
        time_str = task.date_completed.strftime("%H:%M") if task.date_completed else ""
        report.append(f"  ✓ [{task.id}] {task.description} (completed at {time_str})")
    report.append("")
    return "\n".join(report)


def format_summary_report(tasks: List[Task], days: int) -> str:
    if not tasks:
        return f"{Fore.YELLOW}No tasks completed in the last {days} days{Style.RESET_ALL}\n"
    
    report = [f"\n{Fore.CYAN}═══ {days}-DAY SUMMARY ═══{Style.RESET_ALL}\n"]
    report.append(f"Completed {len(tasks)} task(s):\n")
    
    by_day = {}
    for task in tasks:
        if task.date_completed:
            day = task.date_completed.strftime("%Y-%m-%d")
            if day not in by_day:
                by_day[day] = []
            by_day[day].append(task)
    
    for day in sorted(by_day.keys(), reverse=True):
        day_tasks = by_day[day]
        report.append(f"{Fore.BLUE}{day}{Style.RESET_ALL} ({len(day_tasks)} tasks)")
        for task in day_tasks:
            report.append(f"  ✓ {task.description}")
        report.append("")
    
    return "\n".join(report)


def format_week_report(tasks: List[Task]) -> str:
    report = [f"\n{Fore.CYAN}═══ WEEKLY REPORT ═══{Style.RESET_ALL}\n"]
    
    if not tasks:
        report.append(f"{Fore.YELLOW}No tasks completed this week{Style.RESET_ALL}")
    else:
        report.append(f"Completed {len(tasks)} task(s) this week:\n")
        
        by_priority = {Priority.HIGH: [], Priority.MEDIUM: [], Priority.LOW: []}
        for task in tasks:
            by_priority[task.priority].append(task)
        
        for priority in [Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
            if by_priority[priority]:
                color = _get_priority_color(priority)
                report.append(f"{color}{priority.value.upper()} PRIORITY{Style.RESET_ALL} ({len(by_priority[priority])} tasks)")
                for task in by_priority[priority][:5]:
                    report.append(f"  ✓ {task.description}")
                if len(by_priority[priority]) > 5:
                    report.append(f"  ... and {len(by_priority[priority]) - 5} more")
                report.append("")
    
    return "\n".join(report)


def format_stats_report(stats: dict) -> str:
    report = [f"\n{Fore.CYAN}═══ PRODUCTIVITY STATS ({stats['days']} DAYS) ═══{Style.RESET_ALL}\n"]
    
    report.append(f"Total Tasks:      {stats['total_tasks']}")
    report.append(f"Completed:        {stats['completed']}")
    report.append(f"Pending:          {stats['pending']}")
    report.append(f"In Progress:      {stats['working']}")
    report.append(f"Blocked:          {stats['blocked']}")
    report.append(f"Completion Rate:  {stats['completion_rate']:.1f}%")
    
    if stats['avg_completion_hours'] > 0:
        report.append(f"Avg Time:         {stats['avg_completion_hours']:.1f} hours")
    
    report.append("")
    return "\n".join(report)