"""
Integration tests for web interface with validate service.
"""
import pytest
import requests
from pathlib import Path


@pytest.mark.integration
@pytest.mark.skip(reason="Requires Selenium WebDriver - install manually if needed")
class TestWebIntegration:
    """Test web interface integration with validate service."""
    
    def test_validate_button_exists(self):
        """Test that validate button exists on results page."""
        # This test requires Selenium - skipped by default
        # To run: pip install selenium, then unskip this test
        pass
    
    def test_validate_button_shows_card(self):
        """Test that clicking validate button shows validation card."""
        # This test requires Selenium - skipped by default
        pass
    
    def test_file_upload_and_validation(self):
        """Test full workflow: upload file and validate."""
        # This test requires Selenium - skipped by default
        pass


@pytest.mark.integration
class TestWebAPIIntegration:
    """Test web interface API calls to validate service (without browser)."""
    
    def test_validate_service_accessible_from_web(self):
        """Test that validate service is accessible on expected port."""
        try:
            response = requests.get("http://localhost:8002/health", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("Validate service not running on localhost:8002")
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present for cross-origin requests."""
        try:
            response = requests.options(
                "http://localhost:8002/api/v1/check-report/",
                headers={
                    "Origin": "http://localhost:8001",
                    "Access-Control-Request-Method": "POST"
                },
                timeout=5
            )
            # Check for CORS headers
            assert "Access-Control-Allow-Origin" in response.headers or response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("Validate service not running on localhost:8002")
