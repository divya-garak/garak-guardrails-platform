#!/usr/bin/env python3
"""
Test script for the dynamic provider configuration system.

This script tests the core functionality of the provider management system
including provider registration, configuration resolution, and NeMo integration.
"""

import json
import yaml
import tempfile
from pathlib import Path
from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Import our modules
from dynamic_provider import (
    DynamicProviderConfig,
    get_provider_manager,
    validate_provider_config,
    create_dynamic_model_config,
    resolve_dynamic_providers
)
from nemo_integration import NemoGuardrailsIntegration
from config_migrator import ConfigMigrator, migrate_config_file


def test_provider_registration():
    """Test provider registration and management."""
    log.info("Testing provider registration...")
    
    manager = get_provider_manager()
    
    # Test OpenAI provider registration
    openai_config = DynamicProviderConfig(
        provider_name="openai",
        credentials={
            "api_key": "sk-test-key-12345",
            "organization": "test-org"
        },
        model_name="gpt-4",
        parameters={
            "temperature": 0.7,
            "max_tokens": 1000
        }
    )
    
    # Validate configuration
    errors = validate_provider_config(openai_config)
    assert not errors, f"OpenAI config validation failed: {errors}"
    
    # Register provider
    manager.register_provider("test-openai", openai_config)
    
    # Test retrieval
    retrieved_config = manager.get_provider_config("test-openai")
    assert retrieved_config is not None, "Failed to retrieve registered provider"
    assert retrieved_config.provider_name == "openai", "Provider name mismatch"
    assert retrieved_config.model_name == "gpt-4", "Model name mismatch"
    
    # Test credentials retrieval
    credentials = manager.get_credentials("test-openai")
    assert credentials is not None, "Failed to retrieve credentials"
    assert credentials.api_key == "sk-test-key-12345", "API key mismatch"
    
    log.info("✅ Provider registration tests passed")


def test_anthropic_provider():
    """Test Anthropic provider configuration."""
    log.info("Testing Anthropic provider...")
    
    manager = get_provider_manager()
    
    # Test Anthropic provider
    anthropic_config = DynamicProviderConfig(
        provider_name="anthropic",
        credentials={
            "api_key": "sk-ant-test-key-12345"
        },
        model_name="claude-3-5-sonnet-20241022",
        parameters={
            "max_tokens": 1024,
            "temperature": 0.5
        }
    )
    
    # Validate
    errors = validate_provider_config(anthropic_config)
    assert not errors, f"Anthropic config validation failed: {errors}"
    
    # Register
    manager.register_provider("test-anthropic", anthropic_config)
    
    # Test model config generation
    model_config = create_dynamic_model_config("test-anthropic", anthropic_config)
    
    expected_keys = ["type", "engine", "model", "parameters"]
    for key in expected_keys:
        assert key in model_config, f"Missing key in model config: {key}"
    
    assert model_config["engine"] == "anthropic", "Incorrect engine"
    assert model_config["model"] == "claude-3-5-sonnet-20241022", "Incorrect model"
    assert "api_key" in model_config["parameters"], "API key not in parameters"
    
    log.info("✅ Anthropic provider tests passed")


def test_configuration_resolution():
    """Test configuration resolution with dynamic providers."""
    log.info("Testing configuration resolution...")
    
    # Create a test configuration with dynamic providers
    test_config = {
        "colang_version": "2.x",
        "models": [
            {
                "type": "main",
                "engine": "openai",
                "model": "gpt-3.5-turbo"
            },
            {
                "type": "main",
                "provider_config_id": "test-openai"
            },
            {
                "type": "main", 
                "provider_config_id": "test-anthropic"
            }
        ],
        "rails": {
            "input": {
                "flows": ["self check input"]
            }
        }
    }
    
    # Resolve dynamic providers
    resolved_config = resolve_dynamic_providers(test_config)
    
    # Check that dynamic providers were resolved
    assert len(resolved_config["models"]) == 3, "Incorrect number of models"
    
    # First model should be unchanged
    first_model = resolved_config["models"][0]
    assert first_model["engine"] == "openai", "First model should be unchanged"
    
    # Second model should be resolved
    second_model = resolved_config["models"][1]
    assert second_model["engine"] == "openai", "Second model should be resolved to OpenAI"
    assert second_model["model"] == "gpt-4", "Incorrect resolved model name"
    assert "api_key" in second_model["parameters"], "API key missing from resolved model"
    
    # Third model should be resolved to Anthropic
    third_model = resolved_config["models"][2]
    assert third_model["engine"] == "anthropic", "Third model should be resolved to Anthropic"
    assert third_model["model"] == "claude-3-5-sonnet-20241022", "Incorrect Anthropic model name"
    
    log.info("✅ Configuration resolution tests passed")


def test_nemo_integration():
    """Test NeMo Guardrails integration."""
    log.info("Testing NeMo Guardrails integration...")
    
    # Create a temporary config directory
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.yml"
        
        # Create test configuration
        test_config = {
            "colang_version": "2.x",
            "models": [
                {
                    "type": "main",
                    "provider_config_id": "test-openai"
                }
            ]
        }
        
        # Write config
        with open(config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Test integration
        integration = NemoGuardrailsIntegration(str(config_path.parent))
        
        # Test config loading
        loaded_config = integration.load_config()
        assert "models" in loaded_config, "Failed to load config"
        
        # Test provider application
        success = integration.apply_dynamic_providers()
        assert success, "Failed to apply dynamic providers"
        
        # Verify resolved configuration
        resolved_config = integration.load_config()
        resolved_model = resolved_config["models"][0]
        assert resolved_model["engine"] == "openai", "Model not resolved correctly"
        assert "provider_config_id" not in resolved_model, "Provider reference not removed"
        
        # Test validation
        validation = integration.validate_configuration()
        assert validation["valid"], f"Configuration validation failed: {validation['errors']}"
        
    log.info("✅ NeMo Guardrails integration tests passed")


def test_config_migration():
    """Test configuration migration tools."""
    log.info("Testing configuration migration...")
    
    # Create a test configuration with hardcoded credentials
    legacy_config = {
        "colang_version": "1.0",
        "models": [
            {
                "type": "main",
                "engine": "openai",
                "model": "gpt-4",
                "parameters": {
                    "api_key": "sk-hardcoded-key-12345",
                    "temperature": 0.7
                }
            },
            {
                "type": "main",
                "engine": "anthropic", 
                "model": "claude-3-opus-20240229",
                "api_key_env_var": "ANTHROPIC_API_KEY"
            }
        ]
    }
    
    # Test migration
    migrator = ConfigMigrator()
    
    # Analyze configuration
    analysis = migrator.analyze_config(legacy_config)
    assert analysis["total_models"] == 2, "Incorrect model count in analysis"
    assert analysis["static_models"] == 2, "Incorrect static model count"
    assert len(analysis["hardcoded_keys"]) == 1, "Failed to detect hardcoded key"
    assert len(analysis["migration_candidates"]) == 2, "Incorrect migration candidates"
    
    # Create migration plan
    plan = migrator.create_migration_plan(legacy_config)
    assert len(plan["recommended_actions"]) == 2, "Incorrect number of recommended actions"
    assert len(plan["provider_configs_needed"]) == 2, "Incorrect provider configs needed"
    
    # Perform migration
    result = migrator.migrate_config(legacy_config)
    assert result.success, f"Migration failed: {result.errors}"
    assert len(result.changes) > 0, "No changes recorded in migration"
    
    # Verify migrated configuration
    migrated_config = result.migrated_config
    assert "supports_dynamic_providers" in migrated_config.get("metadata", {}), "Migration metadata missing"
    
    for model in migrated_config["models"]:
        assert "provider_config_id" in model, "Model not converted to dynamic provider reference"
        assert "api_key" not in model.get("parameters", {}), "Hardcoded API key not removed"
    
    log.info("✅ Configuration migration tests passed")


def test_error_handling():
    """Test error handling and validation."""
    log.info("Testing error handling...")
    
    # Test invalid provider
    invalid_config = DynamicProviderConfig(
        provider_name="invalid_provider",
        credentials={"api_key": "test"},
        model_name="test-model",
        parameters={}
    )
    
    errors = validate_provider_config(invalid_config)
    assert errors, "Should have validation errors for invalid provider"
    assert "Unsupported provider" in errors[0], "Incorrect error message"
    
    # Test missing required credentials
    missing_creds_config = DynamicProviderConfig(
        provider_name="openai",
        credentials={},  # Missing api_key
        model_name="gpt-4",
        parameters={}
    )
    
    errors = validate_provider_config(missing_creds_config)
    assert errors, "Should have validation errors for missing credentials"
    assert any("Missing required credential: api_key" in error for error in errors), "Missing credential error not found"
    
    # Test unsupported model
    unsupported_model_config = DynamicProviderConfig(
        provider_name="openai",
        credentials={"api_key": "test-key"},
        model_name="unsupported-model-name",
        parameters={}
    )
    
    errors = validate_provider_config(unsupported_model_config)
    assert errors, "Should have validation errors for unsupported model"
    assert any("not supported for provider" in error for error in errors), "Unsupported model error not found"
    
    log.info("✅ Error handling tests passed")


def run_all_tests():
    """Run all test functions."""
    log.info("🧪 Starting dynamic provider system tests...")
    
    try:
        test_provider_registration()
        test_anthropic_provider()
        test_configuration_resolution()
        test_nemo_integration()
        test_config_migration()
        test_error_handling()
        
        log.info("🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        log.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)