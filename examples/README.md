# Examples

This directory contains example scripts demonstrating the production-grade structure.

## Running the Demo

```bash
# From the repository root
PYTHONPATH=. python examples/demo.py
```

## What the Demo Shows

The `demo.py` script demonstrates:

1. **Configuration Setup** - Setting up TEST/DRY_RUN/LIVE modes
2. **Audit Logging** - Recording all operations to an audit trail
3. **Compliance Checking** - Enforcing mode-based restrictions
4. **Data Extraction** - Parsing HTML with CSS selectors
5. **Data Normalization** - Standardizing phone numbers, currency, etc.
6. **Pipeline Orchestration** - Running multi-stage workflows
7. **Audit Review** - Querying and analyzing audit logs

## Expected Output

```
================================================================================
Surplus Funds Recovery Application - Production-Grade Structure Demo
================================================================================

1. Setting up configuration...
   Mode: TEST
   Network: OFF
   ...

Demo Complete!
================================================================================

Summary:
  ✓ Configuration set to TEST mode
  ✓ Compliance checks enforced
  ✓ Data extracted from HTML
  ✓ Data normalized successfully
  ✓ Multi-stage pipeline executed
  ✓ Audit trail recorded
```

## Creating Your Own Examples

Use this structure for your own examples:

```python
from pathlib import Path
from surplus_agents.core.config import Config
from surplus_agents.core.audit.logger import AuditLogger
from surplus_agents.pipelines.orchestrator.pipeline import PipelineOrchestrator

# Setup
config = Config(mode="TEST", network="OFF")
audit_logger = AuditLogger(Path("./audit"), mode=config.mode)

# Your code here...
```
