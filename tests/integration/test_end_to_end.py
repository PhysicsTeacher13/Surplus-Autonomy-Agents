"""Integration tests for end-to-end workflows."""

import pytest
from pathlib import Path
import tempfile

from surplus_agents.pipelines.orchestrator.pipeline import PipelineOrchestrator
from surplus_agents.core.audit.logger import AuditLogger
from surplus_agents.core.compliance.checker import ModeComplianceChecker
from surplus_agents.extraction.extractors.html_extractor import HTMLExtractor
from surplus_agents.extraction.extractors.normalizer import DataNormalizer
from surplus_agents.core.config import Config


@pytest.fixture
def temp_dirs():
    """Create temporary directories for integration tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        yield {
            "artifact": base / "artifacts",
            "audit": base / "audit"
        }


@pytest.mark.integration
def test_end_to_end_data_pipeline(temp_dirs):
    """Test complete data extraction and normalization pipeline."""
    # Setup
    config = Config(
        mode="TEST",
        network="OFF",
        artifact_dir=temp_dirs["artifact"],
        audit_dir=temp_dirs["audit"]
    )
    
    audit_logger = AuditLogger(config.audit_dir, mode=config.mode)
    compliance = ModeComplianceChecker(mode=config.mode)
    
    # Create pipeline
    pipeline = PipelineOrchestrator(
        name="data_extraction_pipeline",
        mode=config.mode,
        audit_logger=audit_logger,
        artifact_dir=config.artifact_dir
    )
    
    # Define stages
    def extract_html(data):
        """Extract data from HTML."""
        html = data.get("html", "")
        extractor = HTMLExtractor(mode=config.mode)
        
        selectors = {
            "name": ".name",
            "amount": ".amount"
        }
        
        result = extractor.extract(html, selectors=selectors)
        return {
            **data,
            "extracted": result["data"]
        }
    
    def normalize_data(data):
        """Normalize extracted data."""
        normalizer = DataNormalizer()
        extracted = data.get("extracted", {})
        
        normalized = {
            "name": normalizer.normalize_text(extracted.get("name", "")),
            "amount": normalizer.normalize_currency(extracted.get("amount", ""))
        }
        
        return {
            **data,
            "normalized": normalized
        }
    
    def validate_compliance(data):
        """Validate compliance rules."""
        # Check that we're not performing restricted actions
        compliance.assert_action_allowed("validate")
        
        return {
            **data,
            "compliance_checked": True
        }
    
    # Add stages
    pipeline.add_stage("extract", extract_html, description="Extract data from HTML")
    pipeline.add_stage("normalize", normalize_data, description="Normalize extracted data")
    pipeline.add_stage("validate", validate_compliance, description="Validate compliance")
    
    # Execute pipeline
    input_data = {
        "html": """
        <html>
            <body>
                <div class="name">  John Doe  </div>
                <div class="amount">$1,234.56</div>
            </body>
        </html>
        """
    }
    
    result = pipeline.execute(input_data)
    
    # Verify results
    assert result["status"] == "ok"
    assert result["output"]["normalized"]["name"] == "John Doe"
    assert result["output"]["normalized"]["amount"] == 1234.56
    assert result["output"]["compliance_checked"] is True
    
    # Verify audit trail
    assert len(audit_logger.entries) > 0
    pipeline_entries = audit_logger.get_entries(object_type="pipeline")
    assert len(pipeline_entries) >= 2  # start + complete
    
    # Verify artifacts
    result_file = config.artifact_dir / "data_extraction_pipeline_result.json"
    assert result_file.exists()


@pytest.mark.integration
def test_mode_enforcement_in_pipeline(temp_dirs):
    """Test that mode restrictions are enforced in pipelines."""
    config = Config(mode="TEST", artifact_dir=temp_dirs["artifact"])
    
    pipeline = PipelineOrchestrator(
        name="restricted_pipeline",
        mode=config.mode,
        artifact_dir=config.artifact_dir
    )
    
    def restricted_action(data):
        """Attempt a restricted action."""
        compliance = ModeComplianceChecker(mode="TEST")
        compliance.assert_action_allowed("send_email")  # Should fail
        return data
    
    pipeline.add_stage("restricted", restricted_action)
    
    result = pipeline.execute({"test": "data"})
    
    # Pipeline should fail due to restricted action
    assert result["status"] == "error"
    assert len(result["stages"]) == 1
    assert result["stages"][0]["status"] == "error"
    assert "send_email" in result["stages"][0]["error"]
    assert "blocked" in result["stages"][0]["error"]


@pytest.mark.integration
def test_multi_stage_error_recovery(temp_dirs):
    """Test error recovery in multi-stage pipeline."""
    config = Config(mode="TEST", artifact_dir=temp_dirs["artifact"])
    
    pipeline = PipelineOrchestrator(
        name="recovery_pipeline",
        mode=config.mode,
        artifact_dir=config.artifact_dir
    )
    
    def stage1(data):
        return {**data, "stage1": "ok"}
    
    def stage2_optional(data):
        raise ValueError("Optional stage failed")
    
    def stage3(data):
        return {**data, "stage3": "ok"}
    
    pipeline.add_stage("stage1", stage1, required=True)
    pipeline.add_stage("stage2", stage2_optional, required=False)
    pipeline.add_stage("stage3", stage3, required=True)
    
    result = pipeline.execute({"input": "test"})
    
    # Should have partial success
    assert result["status"] == "partial"
    assert result["output"]["stage1"] == "ok"
    assert result["output"]["stage3"] == "ok"
    assert len(result["stages"]) == 3


@pytest.mark.integration
def test_data_extraction_normalization_flow(temp_dirs):
    """Test complete data extraction and normalization workflow."""
    html_content = """
    <html>
        <body>
            <div class="address">
                <span class="street">  123 Main St  </span>
                <span class="city">san francisco</span>
                <span class="state">California</span>
                <span class="zip">94102</span>
            </div>
            <div class="phone">(555) 123-4567</div>
        </body>
    </html>
    """
    
    # Extract
    extractor = HTMLExtractor(mode="TEST")
    selectors = {
        "street": ".street",
        "city": ".city",
        "state": ".state",
        "zip": ".zip",
        "phone": ".phone"
    }
    
    extracted = extractor.extract(html_content, selectors=selectors)
    
    # Normalize
    normalizer = DataNormalizer()
    
    address = {
        "street": extracted["data"]["street"],
        "city": extracted["data"]["city"],
        "state": extracted["data"]["state"],
        "zip": extracted["data"]["zip"]
    }
    
    normalized_address = normalizer.normalize_address(address)
    normalized_phone = normalizer.normalize_phone(extracted["data"]["phone"])
    
    # Verify
    assert normalized_address["street"] == "123 Main St"
    assert normalized_address["city"] == "San Francisco"
    assert normalized_address["state"] == "CA"
    assert normalized_address["zip"] == "94102"
    assert normalized_phone == "(555) 123-4567"


@pytest.mark.integration
def test_config_from_environment(temp_dirs, monkeypatch):
    """Test configuration from environment variables."""
    monkeypatch.setenv("SURPLUS_MODE", "DRY_RUN")
    monkeypatch.setenv("SURPLUS_NETWORK", "ON")
    monkeypatch.setenv("SURPLUS_ARTIFACT_DIR", str(temp_dirs["artifact"]))
    monkeypatch.setenv("SURPLUS_AUDIT_DIR", str(temp_dirs["audit"]))
    
    config = Config.from_env()
    
    assert config.mode == "DRY_RUN"
    assert config.network == "ON"
    assert str(config.artifact_dir) == str(temp_dirs["artifact"])
    assert str(config.audit_dir) == str(temp_dirs["audit"])
