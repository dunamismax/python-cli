"""Tests for the file organizer application."""

import pytest
from pathlib import Path
import tempfile
import shutil

from apps.file_organizer.organizer import FileOrganizer


class TestFileOrganizer:
    """Test FileOrganizer class."""
    
    def test_get_file_category(self):
        """Test file category detection."""
        organizer = FileOrganizer()
        
        # Test image files
        assert organizer.get_file_category(Path("image.jpg")) == "images"
        assert organizer.get_file_category(Path("photo.png")) == "images"
        assert organizer.get_file_category(Path("icon.svg")) == "images"
        
        # Test document files
        assert organizer.get_file_category(Path("document.pdf")) == "documents"
        assert organizer.get_file_category(Path("text.txt")) == "documents"
        assert organizer.get_file_category(Path("word.docx")) == "documents"
        
        # Test code files
        assert organizer.get_file_category(Path("script.py")) == "code"
        assert organizer.get_file_category(Path("webpage.html")) == "code"
        assert organizer.get_file_category(Path("app.js")) == "code"
        
        # Test video files
        assert organizer.get_file_category(Path("movie.mp4")) == "videos"
        assert organizer.get_file_category(Path("clip.avi")) == "videos"
        
        # Test audio files
        assert organizer.get_file_category(Path("song.mp3")) == "audio"
        assert organizer.get_file_category(Path("sound.wav")) == "audio"
        
        # Test archives
        assert organizer.get_file_category(Path("archive.zip")) == "archives"
        assert organizer.get_file_category(Path("backup.tar.gz")) == "archives"
        
        # Test executables
        assert organizer.get_file_category(Path("program.exe")) == "executables"
        assert organizer.get_file_category(Path("installer.msi")) == "executables"
        
        # Test spreadsheets
        assert organizer.get_file_category(Path("data.xlsx")) == "spreadsheets"
        assert organizer.get_file_category(Path("table.csv")) == "spreadsheets"
        
        # Test presentations
        assert organizer.get_file_category(Path("slides.pptx")) == "presentations"
        assert organizer.get_file_category(Path("presentation.key")) == "presentations"
        
        # Test unknown file type
        assert organizer.get_file_category(Path("unknown.xyz")) == "others"
        assert organizer.get_file_category(Path("no_extension")) == "others"
    
    def test_organize_by_type(self, sample_files_dir):
        """Test organizing files by type."""
        organizer = FileOrganizer()
        target_dir = sample_files_dir.parent / "organized_by_type"
        
        # Test dry run first
        organized_files = organizer.organize_by_type(
            sample_files_dir, target_dir, dry_run=True
        )
        
        assert "documents" in organized_files
        assert "images" in organized_files
        assert "code" in organized_files
        assert "spreadsheets" in organized_files
        assert "archives" in organized_files
        
        # Target directory should not exist in dry run
        assert not target_dir.exists()
        
        # Test actual organization
        organized_files = organizer.organize_by_type(
            sample_files_dir, target_dir, dry_run=False
        )
        
        # Check that target directory and subdirectories exist
        assert target_dir.exists()
        assert (target_dir / "documents").exists()
        assert (target_dir / "images").exists()
        assert (target_dir / "code").exists()
        assert (target_dir / "spreadsheets").exists()
        assert (target_dir / "archives").exists()
        
        # Check that files were moved
        assert (target_dir / "documents" / "document.txt").exists()
        assert (target_dir / "images" / "image.jpg").exists()
        assert (target_dir / "code" / "script.py").exists()
        assert (target_dir / "spreadsheets" / "data.csv").exists()
        assert (target_dir / "archives" / "archive.zip").exists()
        
        # Original files should be moved
        assert not (sample_files_dir / "document.txt").exists()
        assert not (sample_files_dir / "image.jpg").exists()
    
    def test_organize_by_date(self, sample_files_dir):
        """Test organizing files by date."""
        organizer = FileOrganizer()
        target_dir = sample_files_dir.parent / "organized_by_date"
        
        # Test dry run
        organized_files = organizer.organize_by_date(
            sample_files_dir, target_dir, dry_run=True
        )
        
        assert len(organized_files) > 0
        assert not target_dir.exists()
        
        # Test actual organization
        organized_files = organizer.organize_by_date(
            sample_files_dir, target_dir, dry_run=False
        )
        
        assert target_dir.exists()
        # Should have at least one date directory
        date_dirs = [d for d in target_dir.iterdir() if d.is_dir()]
        assert len(date_dirs) > 0
        
        # Check that date directories follow the format
        for date_dir in date_dirs:
            assert len(date_dir.name.split("-")) == 2  # YYYY-MM format
    
    def test_organize_by_size(self, sample_files_dir):
        """Test organizing files by size."""
        organizer = FileOrganizer()
        target_dir = sample_files_dir.parent / "organized_by_size"
        
        # Test dry run
        organized_files = organizer.organize_by_size(
            sample_files_dir, target_dir, dry_run=True
        )
        
        assert len(organized_files) > 0
        assert not target_dir.exists()
        
        # Test actual organization
        organized_files = organizer.organize_by_size(
            sample_files_dir, target_dir, dry_run=False
        )
        
        assert target_dir.exists()
        # Should have size categories
        size_dirs = [d for d in target_dir.iterdir() if d.is_dir()]
        assert len(size_dirs) > 0
        
        # Check for expected size categories
        size_names = [d.name for d in size_dirs]
        expected_sizes = {"small", "medium", "large", "huge"}
        assert any(size in expected_sizes for size in size_names)
    
    def test_find_duplicates(self, duplicate_files_dir):
        """Test finding duplicate files."""
        organizer = FileOrganizer()
        
        duplicates = organizer.find_duplicates(duplicate_files_dir)
        
        # Should find one set of duplicates (file1.txt, file2.txt, file3.txt)
        assert len(duplicates) == 1
        
        # Each duplicate set should have 3 files
        duplicate_set = list(duplicates.values())[0]
        assert len(duplicate_set) == 3
        
        # Check that the files are the expected ones
        filenames = [f.name for f in duplicate_set]
        assert "file1.txt" in filenames
        assert "file2.txt" in filenames
        assert "file3.txt" in filenames
    
    def test_clean_empty_dirs(self, tmp_path):
        """Test cleaning empty directories."""
        organizer = FileOrganizer()
        
        # Create directory structure with empty directories
        (tmp_path / "empty1").mkdir()
        (tmp_path / "empty2").mkdir()
        (tmp_path / "nonempty").mkdir()
        (tmp_path / "nested" / "empty3").mkdir(parents=True)
        
        # Add a file to make one directory non-empty
        (tmp_path / "nonempty" / "file.txt").write_text("content")
        
        # Test dry run
        removed_dirs = organizer.clean_empty_dirs(tmp_path, dry_run=True)
        
        # Should find empty directories but not remove them
        assert len(removed_dirs) == 3  # empty1, empty2, nested/empty3
        assert (tmp_path / "empty1").exists()
        assert (tmp_path / "empty2").exists()
        assert (tmp_path / "nested" / "empty3").exists()
        
        # Test actual cleanup
        removed_dirs = organizer.clean_empty_dirs(tmp_path, dry_run=False)
        
        # Should remove empty directories
        assert len(removed_dirs) == 3
        assert not (tmp_path / "empty1").exists()
        assert not (tmp_path / "empty2").exists()
        assert not (tmp_path / "nested" / "empty3").exists()
        
        # Non-empty directory should remain
        assert (tmp_path / "nonempty").exists()
        assert (tmp_path / "nonempty" / "file.txt").exists()
    
    def test_get_directory_stats(self, sample_files_dir):
        """Test getting directory statistics."""
        organizer = FileOrganizer()
        
        stats = organizer.get_directory_stats(sample_files_dir)
        
        # Check basic stats
        assert stats["total_files"] > 0
        assert stats["total_size"] > 0
        
        # Check file types
        assert "documents" in stats["file_types"]
        assert "images" in stats["file_types"]
        assert "code" in stats["file_types"]
        assert "spreadsheets" in stats["file_types"]
        assert "archives" in stats["file_types"]
        
        # Check size categories
        assert len(stats["size_categories"]) > 0
        
        # Check file lists
        assert len(stats["largest_files"]) > 0
        assert len(stats["oldest_files"]) > 0
        assert len(stats["newest_files"]) > 0
        
        # Each file list should contain tuples of (path, info)
        for file_path, size_str in stats["largest_files"]:
            assert isinstance(file_path, Path)
            assert isinstance(size_str, str)
            assert "B" in size_str or "KB" in size_str  # Size unit
        
        for file_path, date_str in stats["oldest_files"]:
            assert isinstance(file_path, Path)
            assert isinstance(date_str, str)
            assert "-" in date_str  # Date format
    
    def test_organize_nonexistent_directory(self):
        """Test organizing non-existent directory."""
        organizer = FileOrganizer()
        nonexistent_dir = Path("/nonexistent/directory")
        target_dir = Path("/tmp/target")
        
        with pytest.raises(FileNotFoundError):
            organizer.organize_by_type(nonexistent_dir, target_dir)
        
        with pytest.raises(FileNotFoundError):
            organizer.organize_by_date(nonexistent_dir, target_dir)
        
        with pytest.raises(FileNotFoundError):
            organizer.organize_by_size(nonexistent_dir, target_dir)
        
        with pytest.raises(FileNotFoundError):
            organizer.find_duplicates(nonexistent_dir)
        
        with pytest.raises(FileNotFoundError):
            organizer.clean_empty_dirs(nonexistent_dir)
        
        with pytest.raises(FileNotFoundError):
            organizer.get_directory_stats(nonexistent_dir)
    
    def test_organize_with_name_conflicts(self, tmp_path):
        """Test organizing files with name conflicts."""
        organizer = FileOrganizer()
        
        # Create source directory with duplicate names
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content1")
        (source_dir / "file.txt.bak").write_text("content2")
        
        # Create target directory with existing file
        target_dir = tmp_path / "target"
        target_dir.mkdir()
        documents_dir = target_dir / "documents"
        documents_dir.mkdir()
        (documents_dir / "file.txt").write_text("existing content")
        
        # Organize files
        organized_files = organizer.organize_by_type(
            source_dir, target_dir, dry_run=False
        )
        
        # Check that files were renamed to avoid conflicts
        assert (documents_dir / "file.txt").exists()  # Original
        assert (documents_dir / "file_1.txt").exists()  # Renamed
        assert (documents_dir / "file.txt.bak").exists()  # No conflict
        
        # Check contents
        assert (documents_dir / "file.txt").read_text() == "existing content"
        assert (documents_dir / "file_1.txt").read_text() == "content1"
        assert (documents_dir / "file.txt.bak").read_text() == "content2"