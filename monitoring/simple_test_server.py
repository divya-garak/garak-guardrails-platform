#!/usr/bin/env python3
"""
Simple test server for dynamic provider system
"""

import json
import yaml
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Import our dynamic provider system
try:
    from dynamic_provider import (
        DynamicProviderConfig,
        get_provider_manager,
        validate_provider_config,
        create_dynamic_model_config,
        resolve_dynamic_providers,
        SUPPORTED_PROVIDERS
    )
    log.info("✅ Successfully imported dynamic provider system")
except ImportError as e:
    log.error(f"❌ Failed to import dynamic provider system: {e}")
    exit(1)

# Create FastAPI app
app = FastAPI(
    title="Dynamic Provider Test API",
    description="Test server for the dynamic provider configuration system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ProviderConfigRequest(BaseModel):
    config_id: str
    config: Dict[str, Any]

class TestRequest(BaseModel):
    config_id: str
    test_message: str = "Hello, world!"

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Dynamic Provider Test API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "supported_providers": "/providers/supported",
            "providers": "/providers",
            "test": "/test"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "provider_manager": "available"
    }

@app.get("/providers/supported")
async def get_supported_providers():
    """Get list of supported providers."""
    return {
        "status": "success",
        "providers": SUPPORTED_PROVIDERS
    }

@app.get("/providers")
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
        "count": len(configs),
        "providers": configs
    }

@app.post("/providers")
async def create_provider(request: ProviderConfigRequest):
    """Create a new provider configuration."""
    try:
        # Parse provider configuration
        provider_config = DynamicProviderConfig(**request.config)
        
        # Validate configuration
        errors = validate_provider_config(provider_config)
        if errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Provider configuration validation failed",
                    "errors": errors
                }
            )
        
        # Register the provider
        manager = get_provider_manager()
        manager.register_provider(request.config_id, provider_config)
        
        return {
            "status": "success",
            "message": f"Provider configuration '{request.config_id}' created successfully",
            "config_id": request.config_id,
            "provider": provider_config.provider_name,
            "model": provider_config.model_name
        }
        
    except Exception as e:
        log.error(f"Error creating provider configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/providers/{config_id}")
async def get_provider(config_id: str):
    """Get a specific provider configuration."""
    manager = get_provider_manager()
    provider_config = manager.get_provider_config(config_id)
    
    if not provider_config:
        raise HTTPException(
            status_code=404,
            detail=f"Provider configuration '{config_id}' not found"
        )
    
    return {
        "status": "success",
        "config": {
            "config_id": config_id,
            "provider_name": provider_config.provider_name,
            "model_name": provider_config.model_name,
            "parameters": provider_config.parameters,
        }
    }

@app.delete("/providers/{config_id}")
async def delete_provider(config_id: str):
    """Delete a provider configuration."""
    manager = get_provider_manager()
    
    if manager.remove_provider(config_id):
        return {
            "status": "success",
            "message": f"Provider configuration '{config_id}' deleted successfully"
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Provider configuration '{config_id}' not found"
        )

@app.post("/test/{config_id}")
async def test_provider_config(config_id: str, request: TestRequest):
    """Test a provider configuration by generating a model config."""
    try:
        manager = get_provider_manager()
        provider_config = manager.get_provider_config(config_id)
        
        if not provider_config:
            raise HTTPException(
                status_code=404,
                detail=f"Provider configuration '{config_id}' not found"
            )
        
        # Generate model configuration
        model_config = create_dynamic_model_config(config_id, provider_config)
        
        return {
            "status": "success",
            "message": "Provider configuration test successful",
            "config_id": config_id,
            "provider": provider_config.provider_name,
            "model": provider_config.model_name,
            "generated_model_config": model_config
        }
        
    except Exception as e:
        log.error(f"Error testing provider configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/resolve-config")
async def test_config_resolution(config: Dict[str, Any]):
    """Test configuration resolution with dynamic providers."""
    try:
        resolved_config = resolve_dynamic_providers(config)
        
        return {
            "status": "success",
            "message": "Configuration resolution successful",
            "original_config": config,
            "resolved_config": resolved_config
        }
        
    except Exception as e:
        log.error(f"Error resolving configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    log.info("🚀 Starting Dynamic Provider Test Server...")
    uvicorn.run(
        "simple_test_server:app",
        host="0.0.0.0",
        port=8090,
        reload=True,
        log_level="info"
    )