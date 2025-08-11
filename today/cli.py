#!/usr/bin/env python3
import sys
import click
from colorama import Fore, Style

from .task_manager import TaskManager
from .models import Priority, TaskStatus
from . import display


@click.group()
@click.version_option(version='0.1.0', prog_name='today')
@click.pass_context
def cli(ctx):
    """A simple CLI task manager for daily standups"""
    ctx.ensure_object(dict)
    ctx.obj['manager'] = TaskManager()


@cli.command()
@click.argument('description')
@click.pass_context
def task(ctx, description):
    """Add a new task"""
    description = description.strip()
    if not description:
        click.echo(f"{Fore.RED}✗{Style.RESET_ALL} Task description cannot be empty")
        return
    if len(description) > 200:
        click.echo(f"{Fore.RED}✗{Style.RESET_ALL} Task description too long (max 200 characters)")
        return
    
    manager = ctx.obj['manager']
    task_id = manager.add_task(description)
    click.echo(display.format_task_added(task_id, description))


@cli.command()
@click.option('-p', '--priority', help='Filter by priority (high, medium, low)')
@click.option('-t', '--tag', help='Filter by tag')
@click.option('--completed', is_flag=True, help='Show only completed tasks')
@click.option('--pending', is_flag=True, help='Show only pending tasks')
@click.option('--working', is_flag=True, help='Show only working tasks')
@click.option('--blocked', is_flag=True, help='Show only blocked tasks')
@click.pass_context
def list(ctx, priority, tag, completed, pending, working, blocked):
    """List all current tasks"""
    manager = ctx.obj['manager']
    
    if completed:
        tasks = manager.get_tasks_by_status(TaskStatus.COMPLETED)
    elif pending:
        tasks = manager.get_tasks_by_status(TaskStatus.PENDING)
    elif working:
        tasks = manager.get_tasks_by_status(TaskStatus.WORKING)
    elif blocked:
        tasks = manager.get_tasks_by_status(TaskStatus.BLOCKED)
    else:
        tasks = manager.get_active_tasks()
    
    # Filter by priority
    if priority:
        priority_map = {
            'high': Priority.HIGH, 'h': Priority.HIGH,
            'medium': Priority.MEDIUM, 'med': Priority.MEDIUM, 'm': Priority.MEDIUM,
            'low': Priority.LOW, 'l': Priority.LOW
        }
        priority_enum = priority_map.get(priority.lower())
        if not priority_enum:
            click.echo(f"{Fore.RED}✗{Style.RESET_ALL} Invalid priority filter. Use: high, medium, low")
            return
        tasks = [t for t in tasks if t.priority == priority_enum]
    
    # Filter by tag
    if tag:
        tasks = [t for t in tasks if tag in t.tags]
    
    # Sort by priority then date
    priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
    tasks.sort(key=lambda t: (priority_order[t.priority], -t.date_created.timestamp()))
    
    click.echo(display.format_task_list(tasks))


@cli.command()
@click.argument('task_id', type=int)
@click.pass_context
def done(ctx, task_id):
    """Mark a task as completed"""
    manager = ctx.obj['manager']
    task = manager.get_task(task_id)
    if task:
        if manager.mark_task_done(task_id):
            click.echo(display.format_task_completed(task_id, task.description))
    else:
        click.echo(display.format_task_not_found(task_id))


@cli.command()
@click.argument('task_id', type=int)
@click.pass_context
def working(ctx, task_id):
    """Mark a task as currently being worked on"""
    manager = ctx.obj['manager']
    task = manager.get_task(task_id)
    if task:
        if manager.mark_task_working(task_id):
            click.echo(display.format_task_working(task_id, task.description))
    else:
        click.echo(display.format_task_not_found(task_id))


@cli.command()
@click.argument('task_id', type=int)
@click.argument('reason')
@click.pass_context
def block(ctx, task_id, reason):
    """Block a task with a reason"""
    reason = reason.strip()
    if not reason:
        click.echo(f"{Fore.RED}✗{Style.RESET_ALL} Block reason cannot be empty")
        return
    
    manager = ctx.obj['manager']
    if manager.block_task(task_id, reason):
        click.echo(f"{Fore.RED}⚠{Style.RESET_ALL} Task [{task_id}] blocked: {reason}")
    else:
        click.echo(display.format_task_not_found(task_id))


@cli.command()
@click.argument('task_id', type=int)
@click.pass_context
def unblock(ctx, task_id):
    """Unblock a task"""
    manager = ctx.obj['manager']
    if manager.unblock_task(task_id):
        click.echo(f"{Fore.GREEN}✓{Style.RESET_ALL} Task [{task_id}] unblocked")
    else:
        click.echo(display.format_task_not_found(task_id))


@cli.command()
@click.argument('task_id', type=int)
@click.argument('priority_level')
@click.pass_context
def priority(ctx, task_id, priority_level):
    """Set task priority"""
    priority_map = {
        'high': Priority.HIGH, 'h': Priority.HIGH,
        'medium': Priority.MEDIUM, 'med': Priority.MEDIUM, 'm': Priority.MEDIUM,
        'low': Priority.LOW, 'l': Priority.LOW
    }
    priority_enum = priority_map.get(priority_level.lower())
    if not priority_enum:
        click.echo(f"{Fore.RED}✗{Style.RESET_ALL} Invalid priority. Use: high, medium, low")
        return
    
    manager = ctx.obj['manager']
    if manager.set_task_priority(task_id, priority_enum):
        click.echo(f"{Fore.GREEN}✓{Style.RESET_ALL} Task [{task_id}] priority set to {priority_level}")
    else:
        click.echo(display.format_task_not_found(task_id))


@cli.command()
@click.argument('task_id', type=int)
@click.argument('tag_name')
@click.pass_context
def tag(ctx, task_id, tag_name):
    """Add tag to task"""
    tag_name = tag_name.strip().lower()
    if not tag_name:
        click.echo(f"{Fore.RED}✗{Style.RESET_ALL} Tag cannot be empty")
        return
    if len(tag_name) > 20:
        click.echo(f"{Fore.RED}✗{Style.RESET_ALL} Tag too long (max 20 characters)")
        return
    if not all(c.isalnum() or c in '-_' for c in tag_name):
        click.echo(f"{Fore.RED}✗{Style.RESET_ALL} Tag can only contain letters, numbers, hyphens, and underscores")
        return
    
    manager = ctx.obj['manager']
    if manager.add_task_tag(task_id, tag_name):
        click.echo(f"{Fore.GREEN}✓{Style.RESET_ALL} Tag '{tag_name}' added to task [{task_id}]")
    else:
        click.echo(display.format_task_not_found(task_id))


@cli.command()
@click.pass_context
def standup(ctx):
    """Generate standup report"""
    manager = ctx.obj['manager']
    yesterday = manager.get_yesterday_completed_tasks()
    working = manager.get_today_working_tasks()
    priority = manager.get_today_pending_high_priority_tasks()
    blocked = manager.get_blocked_tasks()
    rolling = manager.get_rolling_tasks()
    
    report = display.format_standup_report(yesterday, working, priority, blocked, rolling)
    click.echo(report)


@cli.command()
@click.pass_context
def yesterday(ctx):
    """Show tasks completed yesterday"""
    manager = ctx.obj['manager']
    tasks = manager.get_yesterday_completed_tasks()
    click.echo(display.format_yesterday_tasks(tasks))


@cli.command()
@click.argument('days', type=int, default=7)
@click.pass_context
def summary(ctx, days):
    """Show summary of past tasks"""
    if days <= 0 or days > 365:
        click.echo(f"{Fore.RED}✗{Style.RESET_ALL} Days must be between 1 and 365")
        return
    
    manager = ctx.obj['manager']
    tasks = manager.get_tasks_completed_in_days(days)
    click.echo(display.format_summary_report(tasks, days))


@cli.command()
@click.argument('days', type=int, default=30)
@click.pass_context
def archive(ctx, days):
    """Archive old completed tasks"""
    if days > 365:
        click.echo(f"{Fore.RED}✗{Style.RESET_ALL} Days must be 365 or less")
        return
    
    manager = ctx.obj['manager']
    count = manager.archive_old_completed_tasks(days)
    click.echo(display.format_archive_result(count, days))


@cli.command()
@click.pass_context
def week(ctx):
    """Show weekly summary"""
    manager = ctx.obj['manager']
    tasks = manager.get_tasks_completed_in_days(7)
    click.echo(display.format_week_report(tasks))


@cli.command()
@click.pass_context
def stats(ctx):
    """Show productivity statistics"""
    manager = ctx.obj['manager']
    stats = manager.get_productivity_stats(30)
    click.echo(display.format_stats_report(stats))


def main():
    try:
        cli(obj={})
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()