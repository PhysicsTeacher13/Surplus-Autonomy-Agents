"""Unit tests for data extractors."""

import pytest
from pathlib import Path
import tempfile

from surplus_agents.extraction.extractors.base import BaseExtractor
from surplus_agents.extraction.extractors.html_extractor import HTMLExtractor
from surplus_agents.extraction.extractors.pdf_extractor import PDFExtractor
from surplus_agents.extraction.extractors.normalizer import DataNormalizer


class TestExtractor(BaseExtractor):
    """Concrete implementation for testing BaseExtractor."""
    
    def extract(self, source, **kwargs):
        return {"data": "test"}


@pytest.mark.unit
def test_base_extractor_initialization():
    """Test base extractor initialization."""
    extractor = TestExtractor(mode="TEST")
    assert extractor.mode == "TEST"


@pytest.mark.unit
def test_base_extractor_validate_output():
    """Test base extractor output validation."""
    extractor = TestExtractor()
    
    # Valid output
    errors = extractor.validate_output({"key": "value"})
    assert len(errors) == 0
    
    # Invalid output (not a dict)
    errors = extractor.validate_output("not a dict")
    assert len(errors) > 0


@pytest.mark.unit
def test_html_extractor_basic():
    """Test basic HTML extraction."""
    extractor = HTMLExtractor(mode="TEST")
    
    html = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Header</h1>
            <p>Content</p>
            <a href="/link1">Link 1</a>
            <a href="/link2">Link 2</a>
        </body>
    </html>
    """
    
    result = extractor.extract(html)
    
    assert result["source_type"] == "html"
    assert "data" in result
    assert result["data"]["title"] == "Test Page"
    assert len(result["data"]["links"]) == 2


@pytest.mark.unit
def test_html_extractor_with_selectors():
    """Test HTML extraction with CSS selectors."""
    extractor = HTMLExtractor(mode="TEST")
    
    html = """
    <html>
        <body>
            <div class="title">Page Title</div>
            <div class="content">Page Content</div>
        </body>
    </html>
    """
    
    selectors = {
        "title": ".title",
        "content": ".content"
    }
    
    result = extractor.extract(html, selectors=selectors)
    
    assert result["data"]["title"] == "Page Title"
    assert result["data"]["content"] == "Page Content"


@pytest.mark.unit
def test_html_extractor_table():
    """Test HTML table extraction."""
    extractor = HTMLExtractor(mode="TEST")
    
    html = """
    <html>
        <body>
            <table>
                <thead>
                    <tr><th>Name</th><th>Value</th></tr>
                </thead>
                <tbody>
                    <tr><td>Item 1</td><td>100</td></tr>
                    <tr><td>Item 2</td><td>200</td></tr>
                </tbody>
            </table>
        </body>
    </html>
    """
    
    result = extractor.extract_table(html)
    
    assert result["source_type"] == "html_table"
    assert len(result["headers"]) == 2
    assert len(result["rows"]) == 2
    assert result["rows"][0] == ["Item 1", "100"]


@pytest.mark.unit
def test_pdf_extractor_basic():
    """Test basic PDF extractor initialization."""
    extractor = PDFExtractor(mode="TEST")
    assert extractor.mode == "TEST"


@pytest.mark.unit
def test_pdf_extractor_file_not_found():
    """Test PDF extractor with non-existent file."""
    extractor = PDFExtractor(mode="TEST")
    
    with pytest.raises(FileNotFoundError):
        extractor.extract("/nonexistent/file.pdf")


@pytest.mark.unit
def test_data_normalizer_text():
    """Test text normalization."""
    normalizer = DataNormalizer()
    
    # Whitespace normalization
    assert normalizer.normalize_text("  hello   world  ") == "hello world"
    assert normalizer.normalize_text("hello\n\nworld") == "hello world"
    
    # Empty string
    assert normalizer.normalize_text("") == ""
    assert normalizer.normalize_text(None) == ""


@pytest.mark.unit
def test_data_normalizer_phone():
    """Test phone number normalization."""
    normalizer = DataNormalizer()
    
    # 10-digit US number
    assert normalizer.normalize_phone("5551234567") == "(555) 123-4567"
    assert normalizer.normalize_phone("(555) 123-4567") == "(555) 123-4567"
    assert normalizer.normalize_phone("555-123-4567") == "(555) 123-4567"
    
    # 11-digit with country code
    assert normalizer.normalize_phone("15551234567") == "+1 (555) 123-4567"
    
    # Invalid format (returns original)
    assert normalizer.normalize_phone("123") == "123"
    
    # None
    assert normalizer.normalize_phone(None) is None


@pytest.mark.unit
def test_data_normalizer_address():
    """Test address normalization."""
    normalizer = DataNormalizer()
    
    address = {
        "street": "  123 Main St  ",
        "city": "san francisco",
        "state": "CA",
        "zip": "94102"
    }
    
    normalized = normalizer.normalize_address(address)
    
    assert normalized["street"] == "123 Main St"
    assert normalized["city"] == "San Francisco"
    assert normalized["state"] == "CA"
    assert normalized["zip"] == "94102"


@pytest.mark.unit
def test_data_normalizer_zip():
    """Test ZIP code normalization."""
    normalizer = DataNormalizer()
    
    # 5-digit
    assert normalizer._normalize_zip("94102") == "94102"
    
    # 9-digit
    assert normalizer._normalize_zip("941021234") == "94102-1234"
    
    # Already formatted
    assert normalizer._normalize_zip("94102-1234") == "94102-1234"


@pytest.mark.unit
def test_data_normalizer_currency():
    """Test currency normalization."""
    normalizer = DataNormalizer()
    
    # Integer
    assert normalizer.normalize_currency(100) == 100.0
    
    # Float
    assert normalizer.normalize_currency(100.50) == 100.50
    
    # String with dollar sign
    assert normalizer.normalize_currency("$100.50") == 100.50
    
    # String with commas
    assert normalizer.normalize_currency("$1,234.56") == 1234.56
    
    # None
    assert normalizer.normalize_currency(None) is None
    
    # Invalid
    assert normalizer.normalize_currency("invalid") is None


@pytest.mark.unit
def test_data_normalizer_date():
    """Test date normalization."""
    normalizer = DataNormalizer()
    
    # Various formats
    assert normalizer.normalize_date("2024-01-15") == "2024-01-15"
    assert normalizer.normalize_date("01/15/2024") == "2024-01-15"
    assert normalizer.normalize_date("January 15, 2024") == "2024-01-15"
    
    # Invalid
    assert normalizer.normalize_date("invalid") is None
    assert normalizer.normalize_date(None) is None
