# Production-Grade Structure Documentation

## Overview

This document describes the production-grade structure for the Surplus Autonomy Agents application. The application is designed to recover surplus funds with a focus on compliance, auditability, and testability.

## Directory Structure

```
surplus_agents/
├── core/                          # Core utilities and base classes
│   ├── audit/                     # Audit logging system
│   │   └── logger.py              # Structured audit trail logging
│   ├── compliance/                # Compliance and policy enforcement
│   │   └── checker.py             # Mode-based compliance checking
│   ├── agent_base.py              # Base agent class
│   ├── config.py                  # Configuration management
│   ├── logging.py                 # Application logging
│   ├── storage.py                 # Artifact storage management
│   └── ...
├── extraction/                    # Data extraction modules
│   └── extractors/
│       ├── base.py                # Base extractor class
│       ├── html_extractor.py      # HTML parsing and extraction
│       ├── pdf_extractor.py       # PDF text extraction
│       └── normalizer.py          # Data normalization utilities
├── crawler/                       # Web scraping modules
│   └── scrapers/
│       ├── base.py                # Base scraper with rate limiting
│       └── county_scraper.py      # County website scraper
├── pipelines/                     # Pipeline orchestration
│   └── orchestrator/
│       └── pipeline.py            # Multi-stage pipeline management
└── agents/                        # Specialized agents
    └── ...

tests/
├── unit/                          # Unit tests
│   ├── audit/
│   ├── compliance/
│   ├── extractors/
│   ├── pipelines/
│   └── scrapers/
└── integration/                   # Integration tests
    └── test_end_to_end.py
```

## Key Components

### 1. Audit Logging (`surplus_agents/core/audit/logger.py`)

Provides structured audit trail logging for all operations.

**Features:**
- Timestamped audit entries
- JSONL format for easy parsing
- Query interface for filtering entries
- Mode-aware logging (TEST/DRY_RUN/LIVE)

**Usage:**
```python
from surplus_agents.core.audit.logger import AuditLogger
from pathlib import Path

audit_logger = AuditLogger(Path("./audit"), mode="TEST")

# Log an action
audit_logger.log(
    action="create",
    actor="extraction_agent",
    object_type="document",
    object_id="doc123",
    result="ok",
    details={"file": "test.pdf"}
)

# Save to file
audit_logger.save("audit.jsonl")

# Query entries
errors = audit_logger.get_entries(result="error")
```

### 2. Compliance Checker (`surplus_agents/core/compliance/checker.py`)

Enforces mode-based restrictions and data validation rules.

**Features:**
- Mode-based action blocking (TEST/DRY_RUN/LIVE)
- Extensible rule-based validation
- Built-in rules for required fields and format validation

**Usage:**
```python
from surplus_agents.core.compliance.checker import ModeComplianceChecker

checker = ModeComplianceChecker(mode="TEST")

# Check if action is allowed
if checker.is_action_allowed("send_email"):
    # Action allowed
    pass

# Assert action is allowed (raises PermissionError if blocked)
checker.assert_action_allowed("send_email")  # Raises error in TEST mode
```

### 3. Data Extractors (`surplus_agents/extraction/extractors/`)

Universal extractors for parsing data from various sources.

**HTML Extractor:**
```python
from surplus_agents.extraction.extractors.html_extractor import HTMLExtractor

extractor = HTMLExtractor(mode="TEST")

# Extract with CSS selectors
selectors = {
    "title": "h1",
    "content": ".main-content"
}
result = extractor.extract(html_content, selectors=selectors)

# Extract table data
table_data = extractor.extract_table(html_content)
```

**Data Normalizer:**
```python
from surplus_agents.extraction.extractors.normalizer import DataNormalizer

normalizer = DataNormalizer()

# Normalize phone numbers
phone = normalizer.normalize_phone("5551234567")  # "(555) 123-4567"

# Normalize addresses
address = normalizer.normalize_address({
    "street": "  123 Main St  ",
    "city": "san francisco",
    "state": "CA",
    "zip": "94102"
})

# Normalize currency
amount = normalizer.normalize_currency("$1,234.56")  # 1234.56
```

### 4. Web Scrapers (`surplus_agents/crawler/scrapers/`)

Scrapers with built-in rate limiting and error handling.

**Usage:**
```python
from surplus_agents.crawler.scrapers.county_scraper import CountyWebsiteScraper
from common.fixtures import FixtureStore

# In TEST mode with fixtures
fixtures = FixtureStore("./fixtures")
scraper = CountyWebsiteScraper(mode="TEST", fixtures=fixtures)

selectors = {
    "title": "h1.title",
    "amount": ".surplus-amount"
}

result = scraper.scrape(
    url="http://example.com",
    fixture_key="html_snapshots/county.html",
    selectors=selectors
)
```

### 5. Pipeline Orchestrator (`surplus_agents/pipelines/orchestrator/pipeline.py`)

Manages multi-stage data processing workflows.

**Features:**
- Stage-by-stage execution
- Error handling and retry logic
- Optional vs. required stages
- Audit logging integration
- Artifact generation

**Usage:**
```python
from surplus_agents.pipelines.orchestrator.pipeline import PipelineOrchestrator
from surplus_agents.core.audit.logger import AuditLogger
from pathlib import Path

# Create pipeline
audit_logger = AuditLogger(Path("./audit"), mode="TEST")
pipeline = PipelineOrchestrator(
    name="data_pipeline",
    mode="TEST",
    audit_logger=audit_logger,
    artifact_dir=Path("./artifacts")
)

# Define stage handlers
def extract_data(input_data):
    # Extract data logic
    return {"extracted": "data"}

def normalize_data(input_data):
    # Normalize data logic
    return {"normalized": input_data["extracted"]}

# Add stages
pipeline.add_stage(
    name="extract",
    handler=extract_data,
    description="Extract data from source",
    required=True
)

pipeline.add_stage(
    name="normalize",
    handler=normalize_data,
    description="Normalize extracted data",
    required=True,
    retry_on_error=True,
    max_retries=3
)

# Execute pipeline
result = pipeline.execute({"input": "data"})

# Check result
if result["status"] == "ok":
    print("Pipeline completed successfully")
    print(result["output"])
```

## Operating Modes

The application supports three operating modes:

### TEST Mode (Default)
- Network: OFF (uses fixtures)
- Blocks all external actions (email, form submission, payments, etc.)
- Safe for development and testing
- All data sourced from fixtures

### DRY_RUN Mode
- Network: Can be ON or OFF
- Blocks external actions (same as TEST)
- Useful for validation without side effects

### LIVE Mode
- Network: ON
- All actions allowed
- Production mode with real external interactions

**Setting Mode:**
```python
from surplus_agents.core.config import Config

# From code
config = Config(mode="TEST", network="OFF")

# From environment variables
import os
os.environ["SURPLUS_MODE"] = "TEST"
os.environ["SURPLUS_NETWORK"] = "OFF"
config = Config.from_env()
```

## Testing

### Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=surplus_agents --cov-report=html

# Run specific test categories
pytest tests/unit/                # Unit tests only
pytest tests/integration/         # Integration tests only
pytest -m unit                    # Tests marked as unit
pytest -m integration             # Tests marked as integration
```

### Test Structure

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
- **Integration Tests** (`tests/integration/`): Test complete workflows

### Coverage

Current test coverage: **79%** (52 tests passing)

## Configuration

### Environment Variables

- `SURPLUS_MODE`: Operating mode (TEST, DRY_RUN, LIVE)
- `SURPLUS_NETWORK`: Network setting (ON, OFF)
- `SURPLUS_ARTIFACT_DIR`: Directory for artifacts
- `SURPLUS_AUDIT_DIR`: Directory for audit logs

### Example Configuration

```python
from surplus_agents.core.config import Config
from pathlib import Path

config = Config(
    mode="TEST",
    network="OFF",
    artifact_dir=Path("./artifacts"),
    audit_dir=Path("./audit")
)

# Use config values
print(config.mode)           # "TEST"
print(config.artifact_dir)   # PosixPath('./artifacts')
```

## Best Practices

1. **Always use TEST or DRY_RUN mode for development and testing**
2. **Use fixtures for deterministic testing**
3. **Log all actions to the audit trail**
4. **Validate compliance before performing restricted actions**
5. **Use pipelines for multi-step workflows**
6. **Normalize data before processing**
7. **Handle errors gracefully with retry logic**

## Python Version Compatibility

- **Minimum:** Python 3.10
- **Tested:** Python 3.12
- **Recommended:** Python 3.11+

## Dependencies

See `requirements.txt` for full list. Key dependencies:

- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `beautifulsoup4>=4.12.0` - HTML parsing
- `lxml>=4.9.0` - XML/HTML processing
- `httpx==0.27.0` - HTTP client
- `pydantic==2.7.4` - Data validation

## Next Steps

For implementing specific agents or extending functionality:

1. Inherit from `BaseAgent` in `common/base_agent.py`
2. Use the extractors, scrapers, and pipeline orchestrator
3. Add comprehensive tests
4. Ensure compliance checks are in place
5. Log all actions to the audit trail
