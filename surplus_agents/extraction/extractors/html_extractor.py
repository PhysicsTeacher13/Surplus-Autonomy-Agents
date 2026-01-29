"""HTML extractor for parsing and extracting data from HTML documents."""

from typing import Any, Dict, Optional
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from .base import BaseExtractor


class HTMLExtractor(BaseExtractor):
    """
    Extracts structured data from HTML documents.
    
    Uses BeautifulSoup for parsing and supports various extraction methods
    like CSS selectors, tag-based searches, and text extraction.
    """
    
    def __init__(self, mode: str = "TEST"):
        """
        Initialize HTML extractor.
        
        Args:
            mode: Operating mode (TEST, DRY_RUN, LIVE)
        """
        super().__init__(mode)
        if BeautifulSoup is None:
            raise ImportError("beautifulsoup4 is required for HTMLExtractor. Install with: pip install beautifulsoup4")
    
    def extract(self, source: Any, **kwargs) -> Dict[str, Any]:
        """
        Extract data from HTML source.
        
        Args:
            source: HTML string or file path
            **kwargs: Additional options:
                - selectors: Dict mapping field names to CSS selectors
                - parser: HTML parser to use (default: "lxml")
                
        Returns:
            Dictionary containing extracted data
        """
        # Determine if source is a file path or string
        if isinstance(source, (str, bytes)) and len(source) < 1000 and not source.strip().startswith('<'):
            # Likely a file path
            try:
                with open(source, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            except FileNotFoundError:
                html_content = source  # Treat as raw HTML
        else:
            html_content = source
        
        parser = kwargs.get('parser', 'lxml')
        soup = BeautifulSoup(html_content, parser)
        
        selectors = kwargs.get('selectors', {})
        extracted = {}
        
        # Extract data using provided selectors
        for field_name, selector in selectors.items():
            element = soup.select_one(selector)
            extracted[field_name] = element.get_text(strip=True) if element else None
        
        # If no selectors provided, extract basic metadata
        if not selectors:
            extracted = {
                'title': soup.title.get_text(strip=True) if soup.title else None,
                'text': soup.get_text(separator=' ', strip=True),
                'links': [a.get('href') for a in soup.find_all('a', href=True)],
                'meta_tags': {
                    meta.get('name', meta.get('property', '')): meta.get('content', '')
                    for meta in soup.find_all('meta') if meta.get('content')
                }
            }
        
        return {
            'source_type': 'html',
            'data': extracted,
            'metadata': {
                'parser': parser,
                'mode': self.mode
            }
        }
    
    def extract_table(self, source: Any, table_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract table data from HTML.
        
        Args:
            source: HTML string or file path
            table_selector: CSS selector for the table (default: first table)
            
        Returns:
            Dictionary with table data as list of rows
        """
        if isinstance(source, (str, bytes)) and len(source) < 1000 and not source.strip().startswith('<'):
            with open(source, 'r', encoding='utf-8') as f:
                html_content = f.read()
        else:
            html_content = source
        
        soup = BeautifulSoup(html_content, 'lxml')
        
        if table_selector:
            table = soup.select_one(table_selector)
        else:
            table = soup.find('table')
        
        if not table:
            return {'rows': [], 'headers': []}
        
        # Extract headers
        headers = []
        header_row = table.find('thead')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        
        # Extract data rows
        rows = []
        tbody = table.find('tbody') or table
        for tr in tbody.find_all('tr'):
            cells = tr.find_all(['td', 'th'])
            if cells:
                row = [cell.get_text(strip=True) for cell in cells]
                rows.append(row)
        
        return {
            'source_type': 'html_table',
            'headers': headers,
            'rows': rows,
            'row_count': len(rows)
        }
