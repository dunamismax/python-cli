"""File organization utilities."""

from pathlib import Path
from typing import Dict, List, Optional, Callable
import shutil
from datetime import datetime
from collections import defaultdict

from shared.utils import sanitize_filename, bytes_to_human
from shared.logging import get_logger


class FileOrganizer:
    """Organizes files based on various criteria."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.file_types = {
            'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'},
            'documents': {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'},
            'spreadsheets': {'.xls', '.xlsx', '.csv', '.ods', '.numbers'},
            'presentations': {'.ppt', '.pptx', '.odp', '.key'},
            'videos': {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'},
            'audio': {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'},
            'archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'},
            'code': {'.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs'},
            'executables': {'.exe', '.msi', '.deb', '.rpm', '.dmg', '.pkg', '.app'},
        }
    
    def get_file_category(self, file_path: Path) -> str:
        """Get the category of a file based on its extension."""
        extension = file_path.suffix.lower()
        
        for category, extensions in self.file_types.items():
            if extension in extensions:
                return category
        
        return 'others'
    
    def organize_by_type(self, source_dir: Path, target_dir: Path, 
                        dry_run: bool = False) -> Dict[str, List[Path]]:
        """Organize files by type into subdirectories."""
        if not source_dir.exists():
            raise FileNotFoundError(f"Source directory {source_dir} does not exist")
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        organized_files = defaultdict(list)
        
        for file_path in source_dir.iterdir():
            if file_path.is_file():
                category = self.get_file_category(file_path)
                category_dir = target_dir / category
                
                if not dry_run:
                    category_dir.mkdir(exist_ok=True)
                    target_path = category_dir / file_path.name
                    
                    # Handle name conflicts
                    if target_path.exists():
                        counter = 1
                        stem = file_path.stem
                        suffix = file_path.suffix
                        while target_path.exists():
                            target_path = category_dir / f"{stem}_{counter}{suffix}"
                            counter += 1
                    
                    shutil.move(str(file_path), str(target_path))
                    organized_files[category].append(target_path)
                    self.logger.info(f"Moved {file_path.name} to {category}/")
                else:
                    organized_files[category].append(file_path)
        
        return dict(organized_files)
    
    def organize_by_date(self, source_dir: Path, target_dir: Path, 
                        date_format: str = "%Y-%m", dry_run: bool = False) -> Dict[str, List[Path]]:
        """Organize files by date into subdirectories."""
        if not source_dir.exists():
            raise FileNotFoundError(f"Source directory {source_dir} does not exist")
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        organized_files = defaultdict(list)
        
        for file_path in source_dir.iterdir():
            if file_path.is_file():
                # Use file modification time
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                date_str = mod_time.strftime(date_format)
                date_dir = target_dir / date_str
                
                if not dry_run:
                    date_dir.mkdir(parents=True, exist_ok=True)
                    target_path = date_dir / file_path.name
                    
                    # Handle name conflicts
                    if target_path.exists():
                        counter = 1
                        stem = file_path.stem
                        suffix = file_path.suffix
                        while target_path.exists():
                            target_path = date_dir / f"{stem}_{counter}{suffix}"
                            counter += 1
                    
                    shutil.move(str(file_path), str(target_path))
                    organized_files[date_str].append(target_path)
                    self.logger.info(f"Moved {file_path.name} to {date_str}/")
                else:
                    organized_files[date_str].append(file_path)
        
        return dict(organized_files)
    
    def organize_by_size(self, source_dir: Path, target_dir: Path, 
                        size_ranges: Optional[List[tuple]] = None, 
                        dry_run: bool = False) -> Dict[str, List[Path]]:
        """Organize files by size into subdirectories."""
        if not source_dir.exists():
            raise FileNotFoundError(f"Source directory {source_dir} does not exist")
        
        if size_ranges is None:
            size_ranges = [
                (0, 1024, "small"),  # < 1KB
                (1024, 1024*1024, "medium"),  # 1KB - 1MB
                (1024*1024, 1024*1024*100, "large"),  # 1MB - 100MB
                (1024*1024*100, float('inf'), "huge"),  # > 100MB
            ]
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        organized_files = defaultdict(list)
        
        for file_path in source_dir.iterdir():
            if file_path.is_file():
                file_size = file_path.stat().st_size
                
                size_category = "unknown"
                for min_size, max_size, category in size_ranges:
                    if min_size <= file_size < max_size:
                        size_category = category
                        break
                
                size_dir = target_dir / size_category
                
                if not dry_run:
                    size_dir.mkdir(exist_ok=True)
                    target_path = size_dir / file_path.name
                    
                    # Handle name conflicts
                    if target_path.exists():
                        counter = 1
                        stem = file_path.stem
                        suffix = file_path.suffix
                        while target_path.exists():
                            target_path = size_dir / f"{stem}_{counter}{suffix}"
                            counter += 1
                    
                    shutil.move(str(file_path), str(target_path))
                    organized_files[size_category].append(target_path)
                    self.logger.info(f"Moved {file_path.name} to {size_category}/")
                else:
                    organized_files[size_category].append(file_path)
        
        return dict(organized_files)
    
    def find_duplicates(self, directory: Path) -> Dict[str, List[Path]]:
        """Find duplicate files in a directory."""
        if not directory.exists():
            raise FileNotFoundError(f"Directory {directory} does not exist")
        
        import hashlib
        
        file_hashes = defaultdict(list)
        
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                # Calculate file hash
                hash_obj = hashlib.md5()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_obj.update(chunk)
                
                file_hash = hash_obj.hexdigest()
                file_hashes[file_hash].append(file_path)
        
        # Return only duplicates
        duplicates = {k: v for k, v in file_hashes.items() if len(v) > 1}
        return duplicates
    
    def clean_empty_dirs(self, directory: Path, dry_run: bool = False) -> List[Path]:
        """Remove empty directories."""
        if not directory.exists():
            raise FileNotFoundError(f"Directory {directory} does not exist")
        
        removed_dirs = []
        
        # Walk from bottom to top to handle nested empty directories
        for dir_path in sorted(directory.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                if not dry_run:
                    dir_path.rmdir()
                    self.logger.info(f"Removed empty directory: {dir_path}")
                removed_dirs.append(dir_path)
        
        return removed_dirs
    
    def get_directory_stats(self, directory: Path) -> Dict:
        """Get statistics about a directory."""
        if not directory.exists():
            raise FileNotFoundError(f"Directory {directory} does not exist")
        
        stats = {
            'total_files': 0,
            'total_size': 0,
            'file_types': defaultdict(int),
            'size_categories': defaultdict(int),
            'largest_files': [],
            'oldest_files': [],
            'newest_files': [],
        }
        
        files_info = []
        
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                file_stat = file_path.stat()
                file_size = file_stat.st_size
                mod_time = datetime.fromtimestamp(file_stat.st_mtime)
                
                stats['total_files'] += 1
                stats['total_size'] += file_size
                
                # File type
                category = self.get_file_category(file_path)
                stats['file_types'][category] += 1
                
                # Size category
                if file_size < 1024:
                    stats['size_categories']['< 1KB'] += 1
                elif file_size < 1024 * 1024:
                    stats['size_categories']['1KB - 1MB'] += 1
                elif file_size < 1024 * 1024 * 100:
                    stats['size_categories']['1MB - 100MB'] += 1
                else:
                    stats['size_categories']['> 100MB'] += 1
                
                files_info.append({
                    'path': file_path,
                    'size': file_size,
                    'modified': mod_time,
                })
        
        # Find largest files
        largest = sorted(files_info, key=lambda x: x['size'], reverse=True)[:10]
        stats['largest_files'] = [(f['path'], bytes_to_human(f['size'])) for f in largest]
        
        # Find oldest files
        oldest = sorted(files_info, key=lambda x: x['modified'])[:10]
        stats['oldest_files'] = [(f['path'], f['modified'].strftime('%Y-%m-%d %H:%M')) for f in oldest]
        
        # Find newest files
        newest = sorted(files_info, key=lambda x: x['modified'], reverse=True)[:10]
        stats['newest_files'] = [(f['path'], f['modified'].strftime('%Y-%m-%d %H:%M')) for f in newest]
        
        return stats