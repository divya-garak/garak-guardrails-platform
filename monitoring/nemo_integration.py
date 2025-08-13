"""
Integration module for connecting dynamic providers with NeMo Guardrails.

This module provides the bridge between the provider management system
and the actual NeMo Guardrails configuration system.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .dynamic_provider import resolve_dynamic_providers, get_provider_manager

log = logging.getLogger(__name__)


class NemoGuardrailsIntegration:
    """Integration layer for NeMo Guardrails dynamic configuration."""
    
    def __init__(self, config_base_path: str = None):
        if config_base_path is None:
            # Default to the main config location
            config_base_path = "/Users/divyachitimalla/garak-guardrails-platform/configs/production/main"
        
        self.config_base_path = Path(config_base_path)
        self.config_file = self.config_base_path / "config.yml"
        self.backup_config_file = self.config_base_path / "config.yml.backup"
        
    def backup_current_config(self) -> bool:
        """Create a backup of the current configuration."""
        try:
            if self.config_file.exists():
                import shutil
                shutil.copy2(self.config_file, self.backup_config_file)
                log.info(f"Config backed up to {self.backup_config_file}")
                return True
            return False
        except Exception as e:
            log.error(f"Failed to backup config: {e}")
            return False
    
    def restore_config_backup(self) -> bool:
        """Restore configuration from backup."""
        try:
            if self.backup_config_file.exists():
                import shutil
                shutil.copy2(self.backup_config_file, self.config_file)
                log.info(f"Config restored from {self.backup_config_file}")
                return True
            return False
        except Exception as e:
            log.error(f"Failed to restore config: {e}")
            return False
    
    def load_config(self) -> Dict[str, Any]:
        """Load the current NeMo Guardrails configuration."""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            log.error(f"Failed to load config: {e}")
            return {}
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to the NeMo Guardrails config file."""
        try:
            # Create directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            log.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            log.error(f"Failed to save config: {e}")
            return False
    
    def apply_dynamic_providers(self) -> bool:
        """Apply dynamic provider configurations to NeMo Guardrails config."""
        try:
            # Backup current config
            self.backup_current_config()
            
            # Load current config
            config = self.load_config()
            
            # Resolve dynamic providers
            resolved_config = resolve_dynamic_providers(config)
            
            # Save the resolved configuration
            success = self.save_config(resolved_config)
            
            if success:
                log.info("Dynamic providers successfully applied to NeMo Guardrails config")
                return True
            else:
                # Restore backup on failure
                self.restore_config_backup()
                return False
                
        except Exception as e:
            log.error(f"Failed to apply dynamic providers: {e}")
            # Try to restore backup
            self.restore_config_backup()
            return False
    
    def add_dynamic_provider_reference(self, config_id: str, model_type: str = "main") -> bool:
        """Add a dynamic provider reference to the NeMo config."""
        try:
            config = self.load_config()
            
            # Ensure models section exists
            if "models" not in config:
                config["models"] = []
            
            # Add provider reference
            provider_ref = {
                "type": model_type,
                "provider_config_id": config_id
            }
            
            # Check if this provider reference already exists
            existing = any(
                model.get("provider_config_id") == config_id 
                for model in config["models"] 
                if isinstance(model, dict)
            )
            
            if not existing:
                config["models"].append(provider_ref)
                return self.save_config(config)
            else:
                log.info(f"Provider reference {config_id} already exists in config")
                return True
                
        except Exception as e:
            log.error(f"Failed to add provider reference: {e}")
            return False
    
    def remove_dynamic_provider_reference(self, config_id: str) -> bool:
        """Remove a dynamic provider reference from the NeMo config."""
        try:
            config = self.load_config()
            
            if "models" not in config:
                return True  # Nothing to remove
            
            # Filter out the provider reference
            original_count = len(config["models"])
            config["models"] = [
                model for model in config["models"]
                if not (isinstance(model, dict) and model.get("provider_config_id") == config_id)
            ]
            
            removed_count = original_count - len(config["models"])
            if removed_count > 0:
                log.info(f"Removed {removed_count} provider references for {config_id}")
                return self.save_config(config)
            else:
                log.info(f"No provider references found for {config_id}")
                return True
                
        except Exception as e:
            log.error(f"Failed to remove provider reference: {e}")
            return False
    
    def get_active_providers(self) -> Dict[str, Any]:
        """Get information about active providers in the current config."""
        try:
            config = self.load_config()
            resolved_config = resolve_dynamic_providers(config)
            
            active_providers = {}
            for model in resolved_config.get("models", []):
                if isinstance(model, dict):
                    engine = model.get("engine")
                    model_name = model.get("model")
                    if engine and model_name:
                        provider_key = f"{engine}_{model_name}"
                        active_providers[provider_key] = {
                            "engine": engine,
                            "model": model_name,
                            "type": model.get("type", "unknown"),
                            "has_api_key": "api_key" in model.get("parameters", {}),
                            "parameters": model.get("parameters", {})
                        }
            
            return active_providers
            
        except Exception as e:
            log.error(f"Failed to get active providers: {e}")
            return {}
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the current configuration."""
        try:
            config = self.load_config()
            resolved_config = resolve_dynamic_providers(config)
            
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "provider_count": 0,
                "dynamic_provider_count": 0
            }
            
            # Count providers
            if "models" in resolved_config:
                validation_result["provider_count"] = len(resolved_config["models"])
                
                # Count dynamic providers in original config
                for model in config.get("models", []):
                    if isinstance(model, dict) and "provider_config_id" in model:
                        validation_result["dynamic_provider_count"] += 1
            
            # Check for missing required fields
            for model in resolved_config.get("models", []):
                if isinstance(model, dict):
                    if not model.get("engine"):
                        validation_result["errors"].append("Model missing 'engine' field")
                        validation_result["valid"] = False
                    
                    if not model.get("model"):
                        validation_result["errors"].append("Model missing 'model' field")
                        validation_result["valid"] = False
            
            return validation_result
            
        except Exception as e:
            log.error(f"Configuration validation failed: {e}")
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "provider_count": 0,
                "dynamic_provider_count": 0
            }


# Global integration instance
_integration = NemoGuardrailsIntegration()


def get_integration() -> NemoGuardrailsIntegration:
    """Get the global integration instance."""
    return _integration


def sync_providers_to_nemo() -> bool:
    """Synchronize all dynamic providers to NeMo Guardrails configuration."""
    return _integration.apply_dynamic_providers()


def add_provider_to_nemo(config_id: str) -> bool:
    """Add a dynamic provider to NeMo Guardrails configuration."""
    return _integration.add_dynamic_provider_reference(config_id)


def remove_provider_from_nemo(config_id: str) -> bool:
    """Remove a dynamic provider from NeMo Guardrails configuration."""
    return _integration.remove_dynamic_provider_reference(config_id)