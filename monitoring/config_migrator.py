"""
Configuration migration tools for dynamic provider system.

This module provides tools to migrate existing NeMo Guardrails configurations
to support dynamic providers and to validate configurations.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .dynamic_provider import SUPPORTED_PROVIDERS

log = logging.getLogger(__name__)


@dataclass
class MigrationResult:
    """Result of a configuration migration."""
    success: bool
    original_config: Dict[str, Any]
    migrated_config: Dict[str, Any]
    changes: List[str]
    warnings: List[str]
    errors: List[str]


class ConfigMigrator:
    """Migrates NeMo Guardrails configurations to support dynamic providers."""
    
    def __init__(self):
        self.supported_engines = set(SUPPORTED_PROVIDERS.keys())
        
    def analyze_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a configuration and identify migration opportunities."""
        analysis = {
            "total_models": 0,
            "static_models": 0,
            "dynamic_refs": 0,
            "migration_candidates": [],
            "hardcoded_keys": [],
            "unsupported_engines": []
        }
        
        models = config.get("models", [])
        analysis["total_models"] = len(models)
        
        for i, model in enumerate(models):
            if not isinstance(model, dict):
                continue
                
            # Check if already a dynamic reference
            if "provider_config_id" in model:
                analysis["dynamic_refs"] += 1
                continue
                
            analysis["static_models"] += 1
            
            engine = model.get("engine")
            model_name = model.get("model")
            
            # Check for migration candidates
            if engine and engine in self.supported_engines:
                # Look for hardcoded API keys
                parameters = model.get("parameters", {})
                if "api_key" in parameters:
                    analysis["hardcoded_keys"].append({
                        "model_index": i,
                        "engine": engine,
                        "model": model_name
                    })
                
                analysis["migration_candidates"].append({
                    "model_index": i,
                    "engine": engine,
                    "model": model_name,
                    "has_hardcoded_key": "api_key" in parameters
                })
            elif engine and engine not in self.supported_engines:
                analysis["unsupported_engines"].append(engine)
        
        return analysis
    
    def create_migration_plan(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a migration plan for a configuration."""
        analysis = self.analyze_config(config)
        
        plan = {
            "analysis": analysis,
            "recommended_actions": [],
            "provider_configs_needed": []
        }
        
        # Generate recommendations
        for candidate in analysis["migration_candidates"]:
            engine = candidate["engine"]
            model_name = candidate["model"]
            
            suggested_config_id = f"{engine}-{model_name}".replace(".", "-").lower()
            
            action = {
                "type": "migrate_to_dynamic",
                "model_index": candidate["model_index"],
                "suggested_config_id": suggested_config_id,
                "provider": engine,
                "model": model_name
            }
            
            plan["recommended_actions"].append(action)
            plan["provider_configs_needed"].append({
                "config_id": suggested_config_id,
                "provider_name": engine,
                "model_name": model_name
            })
        
        return plan
    
    def migrate_config(
        self,
        config: Dict[str, Any],
        migration_plan: Optional[Dict[str, Any]] = None,
        auto_create_config_ids: bool = True
    ) -> MigrationResult:
        """Migrate a configuration to use dynamic providers."""
        result = MigrationResult(
            success=False,
            original_config=config.copy(),
            migrated_config=config.copy(),
            changes=[],
            warnings=[],
            errors=[]
        )
        
        try:
            if migration_plan is None:
                migration_plan = self.create_migration_plan(config)
            
            migrated_config = config.copy()
            models = migrated_config.get("models", [])
            
            # Apply migrations in reverse order to preserve indices
            for action in reversed(migration_plan["recommended_actions"]):
                if action["type"] == "migrate_to_dynamic":
                    model_index = action["model_index"]
                    config_id = action["suggested_config_id"]
                    
                    if model_index < len(models):
                        original_model = models[model_index]
                        
                        # Create new dynamic reference
                        new_model = {
                            "type": original_model.get("type", "main"),
                            "provider_config_id": config_id
                        }
                        
                        # Preserve any additional fields
                        for key, value in original_model.items():
                            if key not in ["engine", "model", "parameters", "api_key_env_var"]:
                                new_model[key] = value
                        
                        models[model_index] = new_model
                        
                        result.changes.append(
                            f"Migrated model {model_index} ({action['provider']}/{action['model']}) "
                            f"to dynamic provider reference: {config_id}"
                        )
            
            # Add metadata to indicate dynamic provider support
            if "metadata" not in migrated_config:
                migrated_config["metadata"] = {}
            
            migrated_config["metadata"]["supports_dynamic_providers"] = True
            migrated_config["metadata"]["migration_timestamp"] = str(datetime.now())
            
            result.migrated_config = migrated_config
            result.success = True
            
            if not result.changes:
                result.warnings.append("No models were migrated - configuration may already use dynamic providers")
            
        except Exception as e:
            result.errors.append(f"Migration failed: {str(e)}")
            result.success = False
        
        return result
    
    def validate_migrated_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a migrated configuration."""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "dynamic_refs": [],
            "missing_providers": []
        }
        
        models = config.get("models", [])
        
        for i, model in enumerate(models):
            if not isinstance(model, dict):
                continue
                
            if "provider_config_id" in model:
                config_id = model["provider_config_id"]
                validation["dynamic_refs"].append({
                    "model_index": i,
                    "config_id": config_id
                })
                
                # Check if provider config exists (would need actual provider manager)
                # For now, just note that it's a dynamic reference
                
        return validation


def migrate_config_file(
    input_path: str,
    output_path: Optional[str] = None,
    backup: bool = True
) -> MigrationResult:
    """Migrate a configuration file to support dynamic providers."""
    input_file = Path(input_path)
    
    if not input_file.exists():
        return MigrationResult(
            success=False,
            original_config={},
            migrated_config={},
            changes=[],
            warnings=[],
            errors=[f"Input file does not exist: {input_path}"]
        )
    
    try:
        # Load configuration
        with open(input_file, 'r') as f:
            config = yaml.safe_load(f) or {}
        
        # Migrate
        migrator = ConfigMigrator()
        result = migrator.migrate_config(config)
        
        if result.success:
            # Determine output path
            if output_path is None:
                output_path = str(input_file)
            
            output_file = Path(output_path)
            
            # Create backup if requested
            if backup and output_file.exists():
                backup_file = output_file.with_suffix(f"{output_file.suffix}.backup")
                import shutil
                shutil.copy2(output_file, backup_file)
                result.changes.append(f"Created backup: {backup_file}")
            
            # Write migrated configuration
            with open(output_file, 'w') as f:
                yaml.dump(result.migrated_config, f, default_flow_style=False, sort_keys=False)
            
            result.changes.append(f"Wrote migrated configuration to: {output_file}")
        
        return result
        
    except Exception as e:
        return MigrationResult(
            success=False,
            original_config={},
            migrated_config={},
            changes=[],
            warnings=[],
            errors=[f"Migration failed: {str(e)}"]
        )


# Import datetime for metadata
from datetime import datetime