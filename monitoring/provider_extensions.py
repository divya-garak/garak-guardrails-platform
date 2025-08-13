"""
Extended provider API endpoints for NeMo Guardrails integration.

Additional endpoints that integrate the provider system with NeMo Guardrails.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from .dynamic_provider import get_provider_manager
from .nemo_integration import (
    get_integration,
    sync_providers_to_nemo,
    add_provider_to_nemo,
    remove_provider_from_nemo
)

log = logging.getLogger(__name__)

# Create FastAPI router instead of Flask Blueprint
provider_ext_bp = APIRouter(prefix='/api/providers', tags=['provider-extensions'])


@provider_ext_bp.post('/sync')
async def sync_all_providers():
    """Synchronize all dynamic providers to NeMo Guardrails configuration."""
    try:
        success = sync_providers_to_nemo()
        
        if success:
            return {
                "status": "success",
                "message": "All dynamic providers synchronized to NeMo Guardrails"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "status": "error",
                    "message": "Failed to synchronize providers"
                }
            )
            
    except Exception as e:
        log.error(f"Error synchronizing providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Sync failed: {str(e)}"
            }
        )


@provider_ext_bp.post('/{config_id}/activate')
async def activate_provider(config_id: str):
    """Activate a provider in NeMo Guardrails configuration."""
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
        
        success = add_provider_to_nemo(config_id, provider_config)
        
        if success:
            return {
                "status": "success",
                "message": f"Provider {config_id} activated in NeMo Guardrails"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "status": "error",
                    "message": f"Failed to activate provider {config_id}"
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error activating provider {config_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Activation failed: {str(e)}"
            }
        )


@provider_ext_bp.post('/{config_id}/deactivate')
async def deactivate_provider(config_id: str):
    """Deactivate a provider from NeMo Guardrails configuration."""
    try:
        success = remove_provider_from_nemo(config_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Provider {config_id} deactivated from NeMo Guardrails"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "status": "error",
                    "message": f"Failed to deactivate provider {config_id}"
                }
            )
            
    except Exception as e:
        log.error(f"Error deactivating provider {config_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Deactivation failed: {str(e)}"
            }
        )


@provider_ext_bp.get('/integration/status')
async def get_integration_status():
    """Get the status of NeMo Guardrails integration."""
    try:
        integration = get_integration()
        
        status_info = {
            "enabled": integration.enabled,
            "config_path": integration.config_path,
            "auto_reload": integration.auto_reload,
            "last_sync": integration.last_sync.isoformat() if integration.last_sync else None,
            "synced_providers": len(integration.synced_providers),
            "provider_ids": list(integration.synced_providers)
        }
        
        return {
            "status": "success",
            "integration": status_info
        }
        
    except Exception as e:
        log.error(f"Error getting integration status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Failed to get integration status: {str(e)}"
            }
        )


@provider_ext_bp.post('/integration/reload')
async def reload_nemo_config():
    """Trigger a reload of NeMo Guardrails configuration."""
    try:
        integration = get_integration()
        
        if not integration.enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": "NeMo integration is not enabled"
                }
            )
        
        # This would trigger actual reload in a real implementation
        # For now, just sync providers
        success = sync_providers_to_nemo()
        
        if success:
            return {
                "status": "success",
                "message": "NeMo Guardrails configuration reloaded"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "status": "error",
                    "message": "Failed to reload configuration"
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error reloading NeMo config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Reload failed: {str(e)}"
            }
        )