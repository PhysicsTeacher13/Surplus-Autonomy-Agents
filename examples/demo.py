#!/usr/bin/env python3
"""
Example demonstration of the production-grade surplus funds recovery application.

This script demonstrates:
1. Configuration setup
2. Audit logging
3. Compliance checking
4. Data extraction and normalization
5. Web scraping with fixtures
6. Pipeline orchestration
"""

from pathlib import Path
import tempfile

from surplus_agents.core.config import Config
from surplus_agents.core.audit.logger import AuditLogger
from surplus_agents.core.compliance.checker import ModeComplianceChecker
from surplus_agents.extraction.extractors.html_extractor import HTMLExtractor
from surplus_agents.extraction.extractors.normalizer import DataNormalizer
from surplus_agents.pipelines.orchestrator.pipeline import PipelineOrchestrator


def main():
    """Run the example demonstration."""
    print("=" * 80)
    print("Surplus Funds Recovery Application - Production-Grade Structure Demo")
    print("=" * 80)
    print()
    
    # 1. Setup Configuration
    print("1. Setting up configuration...")
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Config(
            mode="TEST",
            network="OFF",
            artifact_dir=Path(tmpdir) / "artifacts",
            audit_dir=Path(tmpdir) / "audit"
        )
        print(f"   Mode: {config.mode}")
        print(f"   Network: {config.network}")
        print(f"   Artifact Dir: {config.artifact_dir}")
        print(f"   Audit Dir: {config.audit_dir}")
        print()
        
        # 2. Setup Audit Logging
        print("2. Setting up audit logging...")
        audit_logger = AuditLogger(config.audit_dir, mode=config.mode)
        audit_logger.log(
            action="demo_start",
            actor="demo_script",
            object_type="demo",
            object_id="demo_001",
            result="ok",
            details={"description": "Starting demo"}
        )
        print(f"   Logged {len(audit_logger.entries)} audit entries")
        print()
        
        # 3. Compliance Checking
        print("3. Testing compliance checks...")
        compliance = ModeComplianceChecker(mode=config.mode)
        
        print(f"   Can send email in {config.mode} mode? {compliance.is_action_allowed('send_email')}")
        print(f"   Can read data in {config.mode} mode? {compliance.is_action_allowed('read_data')}")
        
        try:
            compliance.assert_action_allowed("send_email")
        except PermissionError as e:
            print(f"   ✓ Correctly blocked restricted action: {e}")
        print()
        
        # 4. Data Extraction
        print("4. Extracting data from HTML...")
        html_content = """
        <html>
            <body>
                <div class="property">
                    <span class="address">123 Main St, San Francisco, CA 94102</span>
                    <span class="amount">$5,432.10</span>
                    <span class="owner">  John Doe  </span>
                    <span class="phone">555-123-4567</span>
                </div>
            </body>
        </html>
        """
        
        extractor = HTMLExtractor(mode=config.mode)
        selectors = {
            "address": ".address",
            "amount": ".amount",
            "owner": ".owner",
            "phone": ".phone"
        }
        
        extracted = extractor.extract(html_content, selectors=selectors)
        print(f"   Extracted {len(extracted['data'])} fields:")
        for key, value in extracted['data'].items():
            print(f"     {key}: {value}")
        print()
        
        # 5. Data Normalization
        print("5. Normalizing extracted data...")
        normalizer = DataNormalizer()
        
        normalized = {
            "owner": normalizer.normalize_text(extracted['data']['owner']),
            "amount": normalizer.normalize_currency(extracted['data']['amount']),
            "phone": normalizer.normalize_phone(extracted['data']['phone'])
        }
        
        print(f"   Normalized data:")
        for key, value in normalized.items():
            print(f"     {key}: {value}")
        print()
        
        # 6. Pipeline Orchestration
        print("6. Running multi-stage pipeline...")
        pipeline = PipelineOrchestrator(
            name="demo_pipeline",
            mode=config.mode,
            audit_logger=audit_logger,
            artifact_dir=config.artifact_dir
        )
        
        # Define pipeline stages
        def stage_extract(data):
            """Stage 1: Extract data"""
            print("     → Stage 1: Extracting data from HTML")
            extractor = HTMLExtractor(mode=config.mode)
            result = extractor.extract(data['html'], selectors=data['selectors'])
            return {**data, 'extracted': result['data']}
        
        def stage_normalize(data):
            """Stage 2: Normalize data"""
            print("     → Stage 2: Normalizing extracted data")
            normalizer = DataNormalizer()
            extracted = data['extracted']
            
            normalized = {
                'owner': normalizer.normalize_text(extracted.get('owner', '')),
                'amount': normalizer.normalize_currency(extracted.get('amount', '')),
                'phone': normalizer.normalize_phone(extracted.get('phone', ''))
            }
            return {**data, 'normalized': normalized}
        
        def stage_validate(data):
            """Stage 3: Validate compliance"""
            print("     → Stage 3: Validating compliance")
            checker = ModeComplianceChecker(mode=config.mode)
            checker.assert_action_allowed("validate")
            return {**data, 'validated': True}
        
        # Add stages to pipeline
        pipeline.add_stage("extract", stage_extract, description="Extract data from HTML")
        pipeline.add_stage("normalize", stage_normalize, description="Normalize data")
        pipeline.add_stage("validate", stage_validate, description="Validate compliance")
        
        # Execute pipeline
        pipeline_input = {
            'html': html_content,
            'selectors': selectors
        }
        
        result = pipeline.execute(pipeline_input)
        
        print(f"   Pipeline status: {result['status']}")
        print(f"   Stages executed: {len(result['stages'])}")
        print(f"   Duration: {result['metadata']['duration_ms']}ms")
        print()
        
        # 7. Review Audit Trail
        print("7. Reviewing audit trail...")
        audit_logger.log(
            action="demo_complete",
            actor="demo_script",
            object_type="demo",
            object_id="demo_001",
            result="ok",
            details={"pipeline_status": result['status']}
        )
        
        audit_file = audit_logger.save("demo_audit.jsonl")
        print(f"   Total audit entries: {len(audit_logger.entries)}")
        print(f"   Audit file saved: {audit_file}")
        
        # Query audit logs
        pipeline_entries = audit_logger.get_entries(object_type="pipeline")
        print(f"   Pipeline-related entries: {len(pipeline_entries)}")
        
        stage_entries = audit_logger.get_entries(object_type="stage")
        print(f"   Stage-related entries: {len(stage_entries)}")
        print()
        
        # 8. Summary
        print("=" * 80)
        print("Demo Complete!")
        print("=" * 80)
        print()
        print("Summary:")
        print(f"  ✓ Configuration set to {config.mode} mode")
        print(f"  ✓ Compliance checks enforced")
        print(f"  ✓ Data extracted from HTML")
        print(f"  ✓ Data normalized successfully")
        print(f"  ✓ Multi-stage pipeline executed")
        print(f"  ✓ Audit trail recorded ({len(audit_logger.entries)} entries)")
        print()
        print("All components working independently and together!")
        print()


if __name__ == "__main__":
    main()
