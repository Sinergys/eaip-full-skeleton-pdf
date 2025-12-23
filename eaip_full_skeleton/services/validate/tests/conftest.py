"""
Pytest configuration for validate service tests.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def test_docx_file():
    """Fixture providing path to test DOCX file."""
    # Create a minimal valid DOCX file (ZIP with required structure)
    import zipfile
    from io import BytesIO
    
    test_file = Path(__file__).parent / 'test_data' / 'test_report.docx'
    test_file.parent.mkdir(exist_ok=True)
    
    # Create minimal DOCX structure
    with zipfile.ZipFile(str(test_file), 'w', zipfile.ZIP_DEFLATED) as docx:
        # [Content_Types].xml
        docx.writestr('[Content_Types].xml', '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
''')
        
        # _rels/.rels
        docx.writestr('_rels/.rels', '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
''')
        
        # word/document.xml
        docx.writestr('word/document.xml', '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p>
            <w:r>
                <w:t>Тестовый энергоаудит</w:t>
            </w:r>
        </w:p>
    </w:body>
</w:document>
''')
    
    return test_file


@pytest.fixture
def api_base_url():
    """Base URL for validate API."""
    return "http://localhost:8002"
