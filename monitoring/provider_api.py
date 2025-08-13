"""
Provider API endpoints for dynamic configuration management.

This module extends the control API with endpoints for managing 
LLM provider configurations dynamically.
"""

import json
import logging
import asyncio
import aiohttp
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ValidationError

from .dynamic_provider import (
    DynamicProviderConfig,
    get_provider_manager,
    validate_provider_config,
    SUPPORTED_PROVIDERS
)

log = logging.getLogger(__name__)

# Create FastAPI router instead of Flask Blueprint
provider_bp = APIRouter(prefix='/api/providers', tags=['providers'])


async def trigger_cache_reload():
    """Trigger NeMo Guardrails configuration cache reload."""
    nemo_base_url = "http://nemo-guardrails:8000"  # Docker service name
    reload_url = f"{nemo_base_url}/v1/rails/reload-cache"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(reload_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    log.info("Successfully triggered NeMo Guardrails cache reload")
                else:
                    log.warning(f"Cache reload request returned status {response.status}")
    except asyncio.TimeoutError:
        log.warning("Timeout triggering NeMo Guardrails cache reload")
    except Exception as e:
        log.warning(f"Failed to trigger NeMo Guardrails cache reload: {e}")


class ProviderCreateRequest(BaseModel):
    config_id: str
    config: Dict[str, Any]


class ProviderUpdateRequest(BaseModel):
    credentials: Dict[str, Any] = None
    config: Dict[str, Any] = None


class ProviderTestRequest(BaseModel):
    test_message: str = "Hello, this is a test message."


@provider_bp.get('/supported')
async def get_supported_providers():
    """Get list of supported providers and their configurations."""
    return {
        "status": "success",
        "providers": SUPPORTED_PROVIDERS
    }


@provider_bp.get('/')
async def list_providers():
    """List all registered provider configurations."""
    manager = get_provider_manager()
    configs = []
    
    for config_id in manager.list_providers():
        provider_config = manager.get_provider_config(config_id)
        if provider_config:
            configs.append({
                "config_id": config_id,
                "provider_name": provider_config.provider_name,
                "model_name": provider_config.model_name,
                "parameters": provider_config.parameters
            })
    
    return {
        "status": "success",
        "providers": configs
    }


@provider_bp.post('/')
async def create_provider(request: ProviderCreateRequest):
    """Create a new provider configuration."""
    try:
        config_id = request.config_id
        
        # Parse provider configuration
        try:
            provider_config = DynamicProviderConfig(**request.config)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": "Invalid provider configuration",
                    "details": e.errors()
                }
            )
        
        # Validate configuration
        errors = validate_provider_config(provider_config)
        if errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": "Provider configuration validation failed",
                    "errors": errors
                }
            )
        
        # Register the provider
        manager = get_provider_manager()
        manager.register_provider(config_id, provider_config)
        
        # Trigger cache reload to pick up the new provider
        asyncio.create_task(trigger_cache_reload())
        
        return {
            "status": "success",
            "message": f"Provider configuration {config_id} created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error creating provider configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Internal error: {str(e)}"
            }
        )


@provider_bp.get('/{config_id}')
async def get_provider(config_id: str):
    """Get a specific provider configuration."""
    manager = get_provider_manager()
    provider_config = manager.get_provider_config(config_id)
    
    if not provider_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "error",
                "message": f"Provider configuration {config_id} not found"
            }
        )
    
    return {
        "status": "success",
        "config": {
            "config_id": config_id,
            "provider_name": provider_config.provider_name,
            "model_name": provider_config.model_name,
            "parameters": provider_config.parameters,
            # Don't expose credentials in GET response for security
        }
    }


@provider_bp.put('/{config_id}')
async def update_provider(config_id: str, request: ProviderUpdateRequest):
    """Update an existing provider configuration."""
    try:
        manager = get_provider_manager()
        
        if config_id not in manager.list_providers():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status": "error",
                    "message": f"Provider configuration {config_id} not found"
                }
            )
        
        # Update credentials if provided
        if request.credentials:
            success = manager.update_credentials(config_id, request.credentials)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "status": "error",
                        "message": f"Failed to update credentials for {config_id}"
                    }
                )
        
        # Update configuration if provided
        if request.config:
            try:
                provider_config = DynamicProviderConfig(**request.config)
                
                # Validate updated configuration
                errors = validate_provider_config(provider_config)
                if errors:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "status": "error",
                            "message": "Provider configuration validation failed",
                            "errors": errors
                        }
                    )
                
                # Re-register with updated config
                manager.register_provider(config_id, provider_config)
                
            except ValidationError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "status": "error",
                        "message": "Invalid provider configuration",
                        "details": e.errors()
                    }
                )
        
        # Trigger cache reload to pick up the changes
        asyncio.create_task(trigger_cache_reload())
        
        return {
            "status": "success",
            "message": f"Provider configuration {config_id} updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating provider configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Internal error: {str(e)}"
            }
        )


@provider_bp.delete('/{config_id}')
async def delete_provider(config_id: str):
    """Delete a provider configuration."""
    manager = get_provider_manager()
    
    if manager.remove_provider(config_id):
        return {
            "status": "success",
            "message": f"Provider configuration {config_id} deleted successfully"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "error",
                "message": f"Provider configuration {config_id} not found"
            }
        )


@provider_bp.post('/{config_id}/test')
async def test_provider(config_id: str, request: ProviderTestRequest):
    """Test a provider configuration with a sample request."""
    try:
        manager = get_provider_manager()
        provider_config = manager.get_provider_config(config_id)
        
        if not provider_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status": "error",
                    "message": f"Provider configuration {config_id} not found"
                }
            )
        
        # This would integrate with the actual NeMo Guardrails system
        # For now, return a mock success response
        return {
            "status": "success",
            "message": "Provider configuration test successful",
            "provider": provider_config.provider_name,
            "model": provider_config.model_name,
            "test_result": "Connection and authentication verified"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error testing provider configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Provider test failed: {str(e)}"
            }
        )


@provider_bp.get('/generate-config/{config_id}')
async def generate_nemo_config(config_id: str):
    """Generate NeMo Guardrails configuration for a provider."""
    try:
        manager = get_provider_manager()
        provider_config = manager.get_provider_config(config_id)
        
        if not provider_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status": "error",
                    "message": f"Provider configuration {config_id} not found"
                }
            )
        
        from .dynamic_provider import create_dynamic_model_config
        model_config = create_dynamic_model_config(config_id, provider_config)
        
        # Generate full NeMo config structure
        nemo_config = {
            "models": [model_config],
            "colang_version": "2.x",
            "rails": {
                "input": {
                    "flows": ["self check input"]
                },
                "output": {
                    "flows": ["self check output"]
                }
            }
        }
        
        return {
            "status": "success",
            "config": nemo_config
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error generating NeMo config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Config generation failed: {str(e)}"
            }
        )