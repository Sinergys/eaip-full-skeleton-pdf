"""
Simple unit tests for validate service (no server required).
"""
import pytest
from pathlib import Path


class TestValidateStructure:
    """Test validate service structure and configuration."""
    
    def test_main_file_exists(self):
        """Test that main.py exists."""
        main_file = Path(__file__).parent.parent / "main.py"
        assert main_file.exists(), "main.py should exist"
    
    def test_requirements_file_exists(self):
        """Test that requirements.txt exists."""
        req_file = Path(__file__).parent.parent / "requirements.txt"
        assert req_file.exists(), "requirements.txt should exist"
    
    def test_readme_file_exists(self):
        """Test that README.md exists."""
        readme = Path(__file__).parent.parent / "README.md"
        assert readme.exists(), "README.md should exist"
    
    def test_word_validator_readme_exists(self):
        """Test that README_WORD_VALIDATOR.md exists."""
        readme = Path(__file__).parent.parent / "README_WORD_VALIDATOR.md"
        assert readme.exists(), "README_WORD_VALIDATOR.md should exist"
    
    def test_word_validator_readme_has_correct_port(self):
        """Test that README_WORD_VALIDATOR.md uses port 8002."""
        readme = Path(__file__).parent.parent / "README_WORD_VALIDATOR.md"
        content = readme.read_text(encoding='utf-8')
        
        # Should NOT contain port 8003
        assert "8003" not in content, "README should not reference old port 8003"
        
        # Should contain port 8002
        assert "8002" in content, "README should reference correct port 8002"
    
    def test_api_directory_exists(self):
        """Test that api directory exists."""
        api_dir = Path(__file__).parent.parent / "api"
        assert api_dir.exists(), "api directory should exist"
    
    def test_core_directory_exists(self):
        """Test that core directory exists."""
        core_dir = Path(__file__).parent.parent / "core"
        assert core_dir.exists(), "core directory should exist"


class TestDocxFileCreation:
    """Test DOCX file creation fixture."""
    
    def test_create_test_docx_file(self, test_docx_file):
        """Test that test DOCX file is created."""
        assert test_docx_file.exists(), "Test DOCX file should be created"
        assert test_docx_file.suffix == ".docx", "File should have .docx extension"
        assert test_docx_file.stat().st_size > 0, "File should not be empty"
    
    def test_docx_file_is_zip(self, test_docx_file):
        """Test that DOCX file is a valid ZIP archive."""
        import zipfile
        
        assert zipfile.is_zipfile(test_docx_file), "DOCX should be a valid ZIP file"
        
        with zipfile.ZipFile(test_docx_file, 'r') as zip_ref:
            files = zip_ref.namelist()
            assert '[Content_Types].xml' in files, "Should contain [Content_Types].xml"
            assert 'word/document.xml' in files, "Should contain word/document.xml"
