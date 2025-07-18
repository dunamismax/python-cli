"""Todo CLI application main module."""

from datetime import datetime
from typing import Optional, List
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

from .models import TodoList, TodoItem, Priority, Status
from .storage import TodoStorage
from shared.config import init_config
from shared.logging import setup_logging, get_logger

# Initialize CLI app
app = typer.Typer(
    name="todo-cli",
    help="A powerful todo list CLI application",
    add_completion=False,
)
console = Console()

# Initialize storage
storage = TodoStorage()


def get_todo_list() -> TodoList:
    """Get the current todo list."""
    return storage.load()


def save_todo_list(todo_list: TodoList) -> None:
    """Save the todo list."""
    storage.save(todo_list)


def display_item(item: TodoItem) -> None:
    """Display a single todo item."""
    status_colors = {
        Status.PENDING: "yellow",
        Status.IN_PROGRESS: "blue",
        Status.COMPLETED: "green",
        Status.CANCELLED: "red",
    }
    
    priority_colors = {
        Priority.LOW: "green",
        Priority.MEDIUM: "yellow",
        Priority.HIGH: "red",
    }
    
    title = Text(item.title, style="bold")
    
    details = []
    details.append(f"ID: {item.id}")
    details.append(f"Status: {item.status.value}")
    details.append(f"Priority: {item.priority.value}")
    details.append(f"Created: {item.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    if item.description:
        details.append(f"Description: {item.description}")
    
    if item.due_date:
        details.append(f"Due: {item.due_date.strftime('%Y-%m-%d %H:%M')}")
    
    if item.tags:
        details.append(f"Tags: {', '.join(item.tags)}")
    
    if item.completed_at:
        details.append(f"Completed: {item.completed_at.strftime('%Y-%m-%d %H:%M')}")
    
    panel = Panel(
        "\n".join(details),
        title=title,
        border_style=status_colors[item.status],
    )
    
    console.print(panel)


def display_table(items: List[TodoItem]) -> None:
    """Display todo items in a table."""
    if not items:
        console.print("[yellow]No todo items found.[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", justify="right")
    table.add_column("Title", min_width=20)
    table.add_column("Status", justify="center")
    table.add_column("Priority", justify="center")
    table.add_column("Created", justify="center")
    table.add_column("Due", justify="center")
    
    for item in items:
        status_colors = {
            Status.PENDING: "yellow",
            Status.IN_PROGRESS: "blue",
            Status.COMPLETED: "green",
            Status.CANCELLED: "red",
        }
        
        priority_colors = {
            Priority.LOW: "green",
            Priority.MEDIUM: "yellow",
            Priority.HIGH: "red",
        }
        
        due_str = item.due_date.strftime("%m/%d") if item.due_date else "-"
        
        table.add_row(
            str(item.id),
            item.title,
            f"[{status_colors[item.status]}]{item.status.value}[/{status_colors[item.status]}]",
            f"[{priority_colors[item.priority]}]{item.priority.value}[/{priority_colors[item.priority]}]",
            item.created_at.strftime("%m/%d"),
            due_str,
        )
    
    console.print(table)


@app.command()
def add(
    title: str = typer.Argument(..., help="Title of the todo item"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="Description of the todo item"),
    priority: Priority = typer.Option(Priority.MEDIUM, "--priority", "-p", help="Priority level"),
    due_date: Optional[str] = typer.Option(None, "--due", help="Due date (YYYY-MM-DD)"),
    tags: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="Tags for the todo item"),
):
    """Add a new todo item."""
    todo_list = get_todo_list()
    
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            console.print("[red]Invalid date format. Use YYYY-MM-DD.[/red]")
            raise typer.Exit(1)
    
    item = todo_list.add_item(
        title=title,
        description=description,
        priority=priority,
        due_date=parsed_due_date,
        tags=tags or [],
    )
    
    save_todo_list(todo_list)
    console.print(f"[green]Added todo item: {item.title} (ID: {item.id})[/green]")


@app.command()
def list(
    status: Optional[Status] = typer.Option(None, "--status", "-s", help="Filter by status"),
    priority: Optional[Priority] = typer.Option(None, "--priority", "-p", help="Filter by priority"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed view"),
):
    """List todo items."""
    todo_list = get_todo_list()
    items = todo_list.filter_items(status=status, priority=priority, tag=tag)
    
    if detailed:
        for item in items:
            display_item(item)
    else:
        display_table(items)


@app.command()
def show(item_id: int = typer.Argument(..., help="ID of the todo item")):
    """Show details of a specific todo item."""
    todo_list = get_todo_list()
    item = todo_list.get_item(item_id)
    
    if not item:
        console.print(f"[red]Todo item with ID {item_id} not found.[/red]")
        raise typer.Exit(1)
    
    display_item(item)


@app.command()
def complete(item_id: int = typer.Argument(..., help="ID of the todo item")):
    """Mark a todo item as completed."""
    todo_list = get_todo_list()
    item = todo_list.complete_item(item_id)
    
    if not item:
        console.print(f"[red]Todo item with ID {item_id} not found.[/red]")
        raise typer.Exit(1)
    
    save_todo_list(todo_list)
    console.print(f"[green]Completed todo item: {item.title}[/green]")


@app.command()
def update(
    item_id: int = typer.Argument(..., help="ID of the todo item"),
    title: Optional[str] = typer.Option(None, "--title", help="New title"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="New description"),
    priority: Optional[Priority] = typer.Option(None, "--priority", "-p", help="New priority"),
    status: Optional[Status] = typer.Option(None, "--status", "-s", help="New status"),
):
    """Update a todo item."""
    todo_list = get_todo_list()
    
    updates = {}
    if title is not None:
        updates["title"] = title
    if description is not None:
        updates["description"] = description
    if priority is not None:
        updates["priority"] = priority
    if status is not None:
        updates["status"] = status
    
    if not updates:
        console.print("[yellow]No updates specified.[/yellow]")
        return
    
    item = todo_list.update_item(item_id, **updates)
    
    if not item:
        console.print(f"[red]Todo item with ID {item_id} not found.[/red]")
        raise typer.Exit(1)
    
    save_todo_list(todo_list)
    console.print(f"[green]Updated todo item: {item.title}[/green]")


@app.command()
def delete(item_id: int = typer.Argument(..., help="ID of the todo item")):
    """Delete a todo item."""
    todo_list = get_todo_list()
    item = todo_list.get_item(item_id)
    
    if not item:
        console.print(f"[red]Todo item with ID {item_id} not found.[/red]")
        raise typer.Exit(1)
    
    if Confirm.ask(f"Are you sure you want to delete '{item.title}'?"):
        todo_list.delete_item(item_id)
        save_todo_list(todo_list)
        console.print(f"[green]Deleted todo item: {item.title}[/green]")
    else:
        console.print("[yellow]Deletion cancelled.[/yellow]")


@app.command()
def stats():
    """Show todo list statistics."""
    todo_list = get_todo_list()
    stats = todo_list.get_stats()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", justify="left")
    table.add_column("Value", justify="right")
    
    table.add_row("Total Items", str(stats["total"]))
    table.add_row("Completed", str(stats["completed"]))
    table.add_row("Pending", str(stats["pending"]))
    table.add_row("In Progress", str(stats["in_progress"]))
    table.add_row("Completion Rate", f"{stats['completion_rate']:.1f}%")
    
    console.print(table)


@app.command()
def backup():
    """Create a backup of the todo list."""
    backup_path = storage.backup()
    
    if backup_path:
        console.print(f"[green]Backup created: {backup_path}[/green]")
    else:
        console.print("[red]Failed to create backup.[/red]")


@app.command()
def clear():
    """Clear all todo items."""
    if Confirm.ask("Are you sure you want to clear all todo items?"):
        todo_list = TodoList()
        save_todo_list(todo_list)
        console.print("[green]All todo items cleared.[/green]")
    else:
        console.print("[yellow]Clear cancelled.[/yellow]")


def main():
    """Main entry point."""
    # Initialize configuration and logging
    config = init_config()
    setup_logging(
        level=config.log_level,
        log_file=config.logs_dir / "todo_cli.log",
        use_rich=False,  # Don't use rich for CLI apps
    )
    
    app()


if __name__ == "__main__":
    main()