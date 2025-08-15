# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Dynamic provider configuration system for NeMo Guardrails.

This module provides a system for dynamically configuring LLM providers
with user-supplied API keys and settings via API endpoints.
"""

import os
import logging
import json
import redis
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, SecretStr

log = logging.getLogger(__name__)


@dataclass
class ProviderCredentials:
    """Credentials for a specific LLM provider."""
    
    provider: str
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)
    

class DynamicProviderConfig(BaseModel):
    """Configuration for dynamic provider management."""
    
    provider_name: str = Field(description="Name of the LLM provider")
    credentials: Dict[str, Any] = Field(
        default_factory=dict,
        description="Provider credentials and configuration"
    )
    model_name: str = Field(description="Model name to use")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional model parameters"
    )
    
    class Config:
        arbitrary_types_allowed = True


class ProviderManager:
    """Manages dynamic LLM provider configurations."""
    
    def __init__(self, redis_host=None, redis_port=6379, redis_password=None):
        # Try different Redis connection options
        redis_hosts_to_try = [
            redis_host if redis_host else None,
            os.getenv("REDIS_HOST", None),
            "redis",  # Docker service name (try first in containers)
            "deployments-redis-1",  # Docker compose service name
            "localhost",
            "127.0.0.1",
            "redis-service"  # Kubernetes service name
        ]
        
        connected = False
        for host in redis_hosts_to_try:
            if not host:
                continue
            try:
                self.redis_client = redis.Redis(
                    host=host, 
                    port=redis_port, 
                    password=redis_password or os.getenv("REDIS_PASSWORD", "defaultpassword"),
                    decode_responses=True,
                    socket_connect_timeout=1,
                    socket_timeout=1
                )
                # Test the connection
                self.redis_client.ping()
                log.info(f"Connected to Redis at {host}:{redis_port} for provider management")
                connected = True
                break
            except Exception as e:
                log.debug(f"Failed to connect to Redis at {host}: {e}")
                continue
        
        if not connected:
            log.warning("Failed to connect to Redis at any host. Using in-memory storage.")
            self.redis_client = None
            self._providers: Dict[str, ProviderCredentials] = {}
            self._active_configs: Dict[str, DynamicProviderConfig] = {}
        
    def register_provider(
        self, 
        config_id: str, 
        provider_config: DynamicProviderConfig
    ) -> None:
        """Register a new provider configuration."""
        credentials = ProviderCredentials(
            provider=provider_config.provider_name,
            **provider_config.credentials
        )
        
        if self.redis_client:
            # Store in Redis
            self.redis_client.hset(
                "providers:credentials", 
                config_id, 
                json.dumps({
                    "provider": credentials.provider,
                    "api_key": credentials.api_key,
                    "api_base_url": credentials.api_base_url,
                    "additional_params": credentials.additional_params
                })
            )
            self.redis_client.hset(
                "providers:configs", 
                config_id, 
                provider_config.model_dump_json()
            )
        else:
            # Fallback to in-memory storage
            self._providers[config_id] = credentials
            self._active_configs[config_id] = provider_config
        
        log.info(f"Registered dynamic provider config: {config_id}")
        
    def get_provider_config(self, config_id: str) -> Optional[DynamicProviderConfig]:
        """Get provider configuration by ID."""
        if self.redis_client:
            config_json = self.redis_client.hget("providers:configs", config_id)
            if config_json:
                return DynamicProviderConfig.model_validate_json(config_json)
            return None
        else:
            return self._active_configs.get(config_id)
        
    def get_credentials(self, config_id: str) -> Optional[ProviderCredentials]:
        """Get credentials for a provider configuration."""
        if self.redis_client:
            creds_json = self.redis_client.hget("providers:credentials", config_id)
            if creds_json:
                creds_data = json.loads(creds_json)
                return ProviderCredentials(**creds_data)
            return None
        else:
            return self._providers.get(config_id)
        
    def remove_provider(self, config_id: str) -> bool:
        """Remove a provider configuration."""
        if self.redis_client:
            # Remove from Redis
            creds_removed = self.redis_client.hdel("providers:credentials", config_id)
            config_removed = self.redis_client.hdel("providers:configs", config_id)
            if creds_removed or config_removed:
                log.info(f"Removed dynamic provider config: {config_id}")
                return True
            return False
        else:
            if config_id in self._providers:
                del self._providers[config_id]
                del self._active_configs[config_id]
                log.info(f"Removed dynamic provider config: {config_id}")
                return True
            return False
        
    def list_providers(self) -> List[str]:
        """List all registered provider configuration IDs."""
        if self.redis_client:
            return list(self.redis_client.hkeys("providers:configs"))
        else:
            return list(self._active_configs.keys())
        
    def update_credentials(
        self, 
        config_id: str, 
        credentials: Dict[str, Any]
    ) -> bool:
        """Update credentials for an existing provider."""
        if self.redis_client:
            creds_json = self.redis_client.hget("providers:credentials", config_id)
            if creds_json:
                creds_data = json.loads(creds_json)
                # Update the credentials
                for key, value in credentials.items():
                    if key in ["provider", "api_key", "api_base_url"]:
                        creds_data[key] = value
                    else:
                        creds_data["additional_params"][key] = value
                # Save back to Redis
                self.redis_client.hset(
                    "providers:credentials", 
                    config_id, 
                    json.dumps(creds_data)
                )
                return True
            return False
        else:
            if config_id in self._providers:
                provider_creds = self._providers[config_id]
                for key, value in credentials.items():
                    if hasattr(provider_creds, key):
                        setattr(provider_creds, key, value)
                    else:
                        provider_creds.additional_params[key] = value
                return True
            return False


# Global provider manager instance
_provider_manager = ProviderManager()


def get_provider_manager() -> ProviderManager:
    """Get the global provider manager instance."""
    return _provider_manager


def create_dynamic_model_config(
    config_id: str,
    provider_config: DynamicProviderConfig
) -> Dict[str, Any]:
    """Create a model configuration dict for NeMo Guardrails.
    
    This converts a dynamic provider config into the format expected
    by the NeMo Guardrails configuration system.
    """
    credentials = _provider_manager.get_credentials(config_id)
    if not credentials:
        raise ValueError(f"No credentials found for config ID: {config_id}")
    
    # Build the model config
    model_config = {
        "type": "main",
        "engine": credentials.provider,
        "model": provider_config.model_name,
        "parameters": provider_config.parameters.copy()
    }
    
    # Add API key if provided
    if credentials.api_key:
        model_config["parameters"]["api_key"] = credentials.api_key
    
    # Add base URL if provided
    if credentials.api_base_url:
        model_config["parameters"]["base_url"] = credentials.api_base_url
    
    # Add any additional parameters
    model_config["parameters"].update(credentials.additional_params)
    
    return model_config


def resolve_dynamic_providers(config: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve any dynamic provider references in a configuration.
    
    This function scans a NeMo Guardrails config and replaces any
    dynamic provider references with actual provider configurations.
    """
    if "models" not in config:
        return config
    
    resolved_config = config.copy()
    resolved_models = []
    
    for model in config["models"]:
        # Check if this is a dynamic provider reference
        if isinstance(model, dict) and model.get("provider_config_id"):
            config_id = model["provider_config_id"]
            provider_config = _provider_manager.get_provider_config(config_id)
            
            if provider_config:
                # Replace with resolved config
                resolved_model = create_dynamic_model_config(config_id, provider_config)
                # Preserve any additional fields from original model config
                for key, value in model.items():
                    if key not in ["provider_config_id", "type", "engine", "model", "parameters"]:
                        resolved_model[key] = value
                resolved_models.append(resolved_model)
            else:
                log.warning(f"Dynamic provider config not found: {config_id}")
                resolved_models.append(model)
        else:
            resolved_models.append(model)
    
    resolved_config["models"] = resolved_models
    return resolved_config


# Supported provider configurations
SUPPORTED_PROVIDERS = {
    "openai": {
        "required_credentials": ["api_key"],
        "optional_credentials": ["api_base_url", "organization"],
        "supported_models": [
            "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini",
            "gpt-3.5-turbo", "gpt-3.5-turbo-instruct"
        ]
    },
    "anthropic": {
        "required_credentials": ["api_key"],
        "optional_credentials": ["api_base_url"],
        "supported_models": [
            "claude-3-5-sonnet-20241022", "claude-3-opus-20240229",
            "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
        ]
    },
    "azure": {
        "required_credentials": ["api_key", "api_base_url"],
        "optional_credentials": ["api_version"],
        "supported_models": ["azure-gpt-4", "azure-gpt-35-turbo"]
    },
    "huggingface": {
        "required_credentials": [],
        "optional_credentials": ["api_key", "api_base_url"],
        "supported_models": ["mistral-7b", "llama2-7b", "codellama-7b"]
    }
}


def validate_provider_config(provider_config: DynamicProviderConfig) -> List[str]:
    """Validate a provider configuration.
    
    Returns a list of validation errors, empty if valid.
    """
    errors = []
    
    provider_name = provider_config.provider_name
    if provider_name not in SUPPORTED_PROVIDERS:
        errors.append(f"Unsupported provider: {provider_name}")
        return errors
    
    provider_spec = SUPPORTED_PROVIDERS[provider_name]
    credentials = provider_config.credentials
    
    # Check required credentials
    for required_cred in provider_spec["required_credentials"]:
        if required_cred not in credentials or not credentials[required_cred]:
            errors.append(f"Missing required credential: {required_cred}")
    
    # Validate model name
    if provider_config.model_name not in provider_spec["supported_models"]:
        errors.append(
            f"Model {provider_config.model_name} not supported for provider {provider_name}"
        )
    
    return errors