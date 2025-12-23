"""
Integration tests for validate service API.
"""
import pytest
import requests
from pathlib import Path


class TestValidateAPI:
    """Test validate service API endpoints."""
    
    @pytest.fixture(autouse=True)
    def check_server_running(self, api_base_url):
        """Check if validate service is running before tests."""
        try:
            response = requests.get(f"{api_base_url}/health", timeout=2)
            if response.status_code != 200:
                pytest.skip("Validate service not responding correctly")
        except requests.exceptions.ConnectionError:
            pytest.skip("Validate service not running on localhost:8002")
        except requests.exceptions.Timeout:
            pytest.skip("Validate service timeout")
    
    def test_health_endpoint(self, api_base_url):
        """Test /health endpoint."""
        response = requests.get(f"{api_base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data['service'] == 'validate'
        assert data['status'] == 'ok'
    
    def test_check_report_endpoint_exists(self, api_base_url):
        """Test that check-report endpoint exists."""
        # Send request without file (should fail but endpoint should exist)
        response = requests.post(f"{api_base_url}/api/v1/check-report/")
        # Should return 422 (validation error) not 404 (not found)
        assert response.status_code == 422
    
    def test_check_report_with_file(self, api_base_url, test_docx_file):
        """Test document validation with a real file."""
        with open(test_docx_file, 'rb') as f:
            files = {'file': ('test_report.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(
                f"{api_base_url}/api/v1/check-report/",
                files=files,
                timeout=300  # 5 minutes timeout for AI processing
            )
        
        # Check response
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        # Check that we received a file
        assert len(response.content) > 0
        
        # Save validated file for manual inspection
        output_file = Path(__file__).parent / 'test_data' / 'test_report_validated.docx'
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Validated file saved to: {output_file}")
    
    def test_check_report_invalid_file(self, api_base_url):
        """Test validation with invalid file type."""
        # Create a fake txt file
        fake_file = Path(__file__).parent / 'test_data' / 'fake.txt'
        fake_file.parent.mkdir(exist_ok=True)
        fake_file.write_text('This is not a DOCX file')
        
        with open(fake_file, 'rb') as f:
            files = {'file': ('fake.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(
                f"{api_base_url}/api/v1/check-report/",
                files=files
            )
        
        # Should fail validation
        assert response.status_code in [400, 422]
    
    def test_check_report_large_file(self, api_base_url):
        """Test validation rejects files over size limit."""
        # Create a file larger than 100MB (use sparse file for speed)
        large_file = Path(__file__).parent / 'test_data' / 'large.docx'
        large_file.parent.mkdir(exist_ok=True)
        
        # Create 101MB file
        with open(large_file, 'wb') as f:
            f.write(b'x' * (101 * 1024 * 1024))
        
        try:
            with open(large_file, 'rb') as f:
                files = {'file': ('large.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                response = requests.post(
                    f"{api_base_url}/api/v1/check-report/",
                    files=files,
                    timeout=10
                )
            
            # Should reject large file
            assert response.status_code in [400, 413, 422]
        finally:
            # Cleanup
            if large_file.exists():
                large_file.unlink()
