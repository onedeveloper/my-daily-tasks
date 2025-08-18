#!/usr/bin/env python3
import sys
import click
from colorama import Fore, Style

from .task_manager import TaskManager
from .models import TaskStatus
from . import display


def handle_task_or_list(ctx, args):
    """Handle both task addition and listing logic"""
    if args:
        # Add a new task
        description = ' '.join(args).strip()
        if not description:
            click.echo(f"{Fore.RED}✗{Style.RESET_ALL} Task description cannot be empty")
            return
        if len(description) > 200:
            click.echo(f"{Fore.RED}✗{Style.RESET_ALL} Task description too long (max 200 characters)")
            return
        
        manager = ctx.obj['manager']
        task_id = manager.add_task(description)
        click.echo(display.format_task_added(task_id, description))
    else:
        # Show task list
        manager = ctx.obj['manager']
        tasks = manager.get_active_tasks()
        
        # Sort by creation date (newest first)
        tasks.sort(key=lambda t: t.date_created, reverse=True)
        
        click.echo(display.format_task_list(tasks))


@click.group(invoke_without_command=True)
@click.version_option(version='1.0.0', prog_name='today')
@click.option('--date', help='Simulate a specific date (YYYY-MM-DD)')
@click.pass_context
def cli(ctx, date):
    """A simple CLI task manager for daily standups"""
    ctx.ensure_object(dict)
    ctx.obj['manager'] = TaskManager(simulated_date=date)
    ctx.obj['date'] = date
    
    # Only run this logic if no subcommand was invoked
    if ctx.invoked_subcommand is None:
        handle_task_or_list(ctx, [])


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
@click.pass_context
def standup(ctx):
    """Generate standup report"""
    manager = ctx.obj['manager']
    yesterday = manager.get_yesterday_worked_tasks()
    today = manager.get_today_working_tasks()
    
    report = display.format_standup_report(yesterday, today)
    click.echo(report)


def main():
    import sys
    
    # List of known commands
    known_commands = ['done', 'standup']
    
    # Check if first non-option argument is a known command
    args = sys.argv[1:]
    first_non_option = None
    
    for arg in args:
        if not arg.startswith('-'):
            first_non_option = arg
            break
    
    # If first argument is not a known command and not empty, treat as task description
    if first_non_option and first_non_option not in known_commands:
        # This should be a task description
        task_args = []
        for arg in args:
            if not arg.startswith('-') and arg not in ['--help', '--version']:
                task_args.append(arg)
        
        if task_args:
            # Handle task creation directly
            from .task_manager import TaskManager
            manager = TaskManager()
            description = ' '.join(task_args).strip()
            
            if len(description) > 200:
                click.echo(f"{Fore.RED}✗{Style.RESET_ALL} Task description too long (max 200 characters)")
                sys.exit(1)
            
            task_id = manager.add_task(description)
            click.echo(display.format_task_added(task_id, description))
            return
    
    # Otherwise, handle normally with Click
    try:
        cli(obj={})
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()