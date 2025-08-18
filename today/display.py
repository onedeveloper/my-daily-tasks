from typing import List
from datetime import datetime
from colorama import Fore, Style, init
from tabulate import tabulate

from .models import Task, TaskStatus

init(autoreset=True)


def format_task_added(task_id: int, description: str) -> str:
    return f"{Fore.GREEN}✓{Style.RESET_ALL} Task [{task_id}] added: {description}"


def format_task_completed(task_id: int, description: str) -> str:
    return f"{Fore.GREEN}✓{Style.RESET_ALL} Task [{task_id}] completed: {description}"


def format_task_not_found(task_id: int) -> str:
    return f"{Fore.RED}✗{Style.RESET_ALL} Task [{task_id}] not found"


def _get_status_icon(status: TaskStatus) -> str:
    icons = {
        TaskStatus.PENDING: f"{Fore.YELLOW}⚡{Style.RESET_ALL}",
        TaskStatus.COMPLETED: f"{Fore.GREEN}✓{Style.RESET_ALL}"
    }
    return icons.get(status, "?")


def format_task_list(tasks: List[Task]) -> str:
    if not tasks:
        return f"{Fore.YELLOW}No tasks found{Style.RESET_ALL}"
    
    headers = ["ID", "Status", "Description", "Created"]
    rows = []
    
    for task in tasks:
        status_icon = _get_status_icon(task.status)
        created = task.date_created.strftime("%Y-%m-%d %H:%M")
        rows.append([task.id, status_icon, task.description, created])
    
    return tabulate(rows, headers=headers, tablefmt="simple")


def format_standup_report(yesterday_worked: List[Task], today_working: List[Task]) -> str:
    report = []
    report.append(f"\n{Fore.CYAN}═══ STANDUP REPORT ═══{Style.RESET_ALL}\n")
    
    # Yesterday section
    report.append(f"\n{Fore.GREEN}▶ YESTERDAY{Style.RESET_ALL}")
    if yesterday_worked:
        for task in yesterday_worked:
            if task.status == TaskStatus.COMPLETED:
                report.append(f"  ✓ {task.description} (completed)")
            else:
                report.append(f"  • {task.description} (worked on)")
    else:
        report.append(f"  {Fore.YELLOW}No tasks worked on yesterday{Style.RESET_ALL}")
    
    # Today section
    report.append(f"\n{Fore.BLUE}▶ TODAY{Style.RESET_ALL}")
    if today_working:
        for task in today_working:
            if task.status == TaskStatus.COMPLETED:
                report.append(f"  ✓ {task.description} (completed)")
            else:
                report.append(f"  ⚡ {task.description} (in progress)")
    else:
        report.append(f"  {Fore.YELLOW}No tasks for today{Style.RESET_ALL}")
    
    return "\n".join(report)