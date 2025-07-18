"""File organizer CLI application main module."""

from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.tree import Tree

from .organizer import FileOrganizer
from shared.config import init_config
from shared.logging import setup_logging, get_logger
from shared.utils import bytes_to_human

# Initialize CLI app
app = typer.Typer(
    name="file-organizer",
    help="A powerful file organization CLI tool",
    add_completion=False,
)
console = Console()


@app.command()
def organize_by_type(
    source: Path = typer.Argument(..., help="Source directory to organize"),
    target: Optional[Path] = typer.Option(None, "--target", "-t", help="Target directory (default: source/organized)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be done without actually moving files"),
):
    """Organize files by type into subdirectories."""
    if target is None:
        target = source / "organized"
    
    organizer = FileOrganizer()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Organizing files by type...", total=None)
            
            organized_files = organizer.organize_by_type(source, target, dry_run=dry_run)
        
        # Display results
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Category", justify="left")
        table.add_column("Files", justify="right")
        
        total_files = 0
        for category, files in organized_files.items():
            table.add_row(category.title(), str(len(files)))
            total_files += len(files)
        
        table.add_row("[bold]Total[/bold]", f"[bold]{total_files}[/bold]")
        
        console.print(table)
        
        if dry_run:
            console.print("\n[yellow]This was a dry run. No files were actually moved.[/yellow]")
        else:
            console.print(f"\n[green]Successfully organized {total_files} files into {target}[/green]")
    
    except Exception as e:
        console.print(f"[red]Error organizing files: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def organize_by_date(
    source: Path = typer.Argument(..., help="Source directory to organize"),
    target: Optional[Path] = typer.Option(None, "--target", "-t", help="Target directory (default: source/organized)"),
    date_format: str = typer.Option("%Y-%m", "--format", "-f", help="Date format for directory names"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be done without actually moving files"),
):
    """Organize files by date into subdirectories."""
    if target is None:
        target = source / "organized"
    
    organizer = FileOrganizer()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Organizing files by date...", total=None)
            
            organized_files = organizer.organize_by_date(source, target, date_format, dry_run=dry_run)
        
        # Display results
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Date", justify="left")
        table.add_column("Files", justify="right")
        
        total_files = 0
        for date_str, files in sorted(organized_files.items()):
            table.add_row(date_str, str(len(files)))
            total_files += len(files)
        
        table.add_row("[bold]Total[/bold]", f"[bold]{total_files}[/bold]")
        
        console.print(table)
        
        if dry_run:
            console.print("\n[yellow]This was a dry run. No files were actually moved.[/yellow]")
        else:
            console.print(f"\n[green]Successfully organized {total_files} files into {target}[/green]")
    
    except Exception as e:
        console.print(f"[red]Error organizing files: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def organize_by_size(
    source: Path = typer.Argument(..., help="Source directory to organize"),
    target: Optional[Path] = typer.Option(None, "--target", "-t", help="Target directory (default: source/organized)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be done without actually moving files"),
):
    """Organize files by size into subdirectories."""
    if target is None:
        target = source / "organized"
    
    organizer = FileOrganizer()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Organizing files by size...", total=None)
            
            organized_files = organizer.organize_by_size(source, target, dry_run=dry_run)
        
        # Display results
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Size Category", justify="left")
        table.add_column("Files", justify="right")
        
        total_files = 0
        for category, files in organized_files.items():
            table.add_row(category.title(), str(len(files)))
            total_files += len(files)
        
        table.add_row("[bold]Total[/bold]", f"[bold]{total_files}[/bold]")
        
        console.print(table)
        
        if dry_run:
            console.print("\n[yellow]This was a dry run. No files were actually moved.[/yellow]")
        else:
            console.print(f"\n[green]Successfully organized {total_files} files into {target}[/green]")
    
    except Exception as e:
        console.print(f"[red]Error organizing files: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def find_duplicates(
    directory: Path = typer.Argument(..., help="Directory to search for duplicates"),
    remove: bool = typer.Option(False, "--remove", "-r", help="Remove duplicate files (keep the first one)"),
):
    """Find and optionally remove duplicate files."""
    organizer = FileOrganizer()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Finding duplicate files...", total=None)
            
            duplicates = organizer.find_duplicates(directory)
        
        if not duplicates:
            console.print("[green]No duplicate files found.[/green]")
            return
        
        # Display duplicates
        total_duplicates = sum(len(files) - 1 for files in duplicates.values())
        console.print(f"\n[yellow]Found {len(duplicates)} sets of duplicates ({total_duplicates} duplicate files)[/yellow]")
        
        for i, (file_hash, files) in enumerate(duplicates.items(), 1):
            console.print(f"\n[bold]Duplicate Set {i}:[/bold]")
            tree = Tree(f"Hash: {file_hash[:8]}...")
            
            for j, file_path in enumerate(files):
                file_stat = file_path.stat()
                size_str = bytes_to_human(file_stat.st_size)
                
                if j == 0:
                    tree.add(f"[green]✓ {file_path.name}[/green] ({size_str}) - [bold]ORIGINAL[/bold]")
                else:
                    tree.add(f"[red]✗ {file_path.name}[/red] ({size_str}) - [bold]DUPLICATE[/bold]")
            
            console.print(tree)
        
        if remove:
            if Confirm.ask(f"Are you sure you want to remove {total_duplicates} duplicate files?"):
                removed_count = 0
                for files in duplicates.values():
                    # Keep the first file, remove the rest
                    for file_path in files[1:]:
                        file_path.unlink()
                        removed_count += 1
                        console.print(f"[red]Removed: {file_path}[/red]")
                
                console.print(f"\n[green]Successfully removed {removed_count} duplicate files.[/green]")
            else:
                console.print("[yellow]Removal cancelled.[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error finding duplicates: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def clean_empty(
    directory: Path = typer.Argument(..., help="Directory to clean empty subdirectories from"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be done without actually removing directories"),
):
    """Remove empty directories."""
    organizer = FileOrganizer()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Cleaning empty directories...", total=None)
            
            removed_dirs = organizer.clean_empty_dirs(directory, dry_run=dry_run)
        
        if not removed_dirs:
            console.print("[green]No empty directories found.[/green]")
            return
        
        console.print(f"\n[yellow]{'Would remove' if dry_run else 'Removed'} {len(removed_dirs)} empty directories:[/yellow]")
        
        for dir_path in removed_dirs:
            console.print(f"  [red]✗ {dir_path}[/red]")
        
        if dry_run:
            console.print("\n[yellow]This was a dry run. No directories were actually removed.[/yellow]")
        else:
            console.print(f"\n[green]Successfully removed {len(removed_dirs)} empty directories.[/green]")
    
    except Exception as e:
        console.print(f"[red]Error cleaning empty directories: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def stats(
    directory: Path = typer.Argument(..., help="Directory to analyze"),
):
    """Show statistics about a directory."""
    organizer = FileOrganizer()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing directory...", total=None)
            
            stats = organizer.get_directory_stats(directory)
        
        # Overview
        overview_table = Table(show_header=True, header_style="bold magenta", title="Directory Overview")
        overview_table.add_column("Metric", justify="left")
        overview_table.add_column("Value", justify="right")
        
        overview_table.add_row("Total Files", str(stats['total_files']))
        overview_table.add_row("Total Size", bytes_to_human(stats['total_size']))
        
        console.print(overview_table)
        
        # File types
        if stats['file_types']:
            console.print("\n[bold magenta]File Types:[/bold magenta]")
            types_table = Table(show_header=True, header_style="bold magenta")
            types_table.add_column("Type", justify="left")
            types_table.add_column("Count", justify="right")
            
            for file_type, count in sorted(stats['file_types'].items()):
                types_table.add_row(file_type.title(), str(count))
            
            console.print(types_table)
        
        # Size categories
        if stats['size_categories']:
            console.print("\n[bold magenta]Size Categories:[/bold magenta]")
            size_table = Table(show_header=True, header_style="bold magenta")
            size_table.add_column("Size Range", justify="left")
            size_table.add_column("Count", justify="right")
            
            for size_cat, count in stats['size_categories'].items():
                size_table.add_row(size_cat, str(count))
            
            console.print(size_table)
        
        # Largest files
        if stats['largest_files']:
            console.print("\n[bold magenta]Largest Files:[/bold magenta]")
            largest_table = Table(show_header=True, header_style="bold magenta")
            largest_table.add_column("File", justify="left")
            largest_table.add_column("Size", justify="right")
            
            for file_path, size_str in stats['largest_files']:
                largest_table.add_row(file_path.name, size_str)
            
            console.print(largest_table)
        
        # Newest files
        if stats['newest_files']:
            console.print("\n[bold magenta]Newest Files:[/bold magenta]")
            newest_table = Table(show_header=True, header_style="bold magenta")
            newest_table.add_column("File", justify="left")
            newest_table.add_column("Modified", justify="right")
            
            for file_path, mod_time in stats['newest_files']:
                newest_table.add_row(file_path.name, mod_time)
            
            console.print(newest_table)
    
    except Exception as e:
        console.print(f"[red]Error analyzing directory: {e}[/red]")
        raise typer.Exit(1)


def main():
    """Main entry point."""
    # Initialize configuration and logging
    config = init_config()
    setup_logging(
        level=config.log_level,
        log_file=config.logs_dir / "file_organizer.log",
        use_rich=False,  # Don't use rich for CLI apps
    )
    
    app()


if __name__ == "__main__":
    main()