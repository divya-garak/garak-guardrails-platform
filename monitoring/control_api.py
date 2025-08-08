#!/usr/bin/env python3
"""
Guardrails Control API
Provides REST API endpoints for dynamic guardrail control
"""

import os
import json
import yaml
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configuration
CONFIG_PATH = "/Users/divyachitimalla/NeMo-Guardrails/comprehensive-config/config.yml"
SERVICES = {
    "main": "http://localhost:8000",
    "jailbreak": "http://localhost:1337", 
    "presidio": "http://localhost:5001",
    "content_safety": "http://localhost:5002"
}

app = FastAPI(
    title="NeMo Guardrails Control API",
    description="Dynamic control and monitoring of guardrail services",
    version="1.0.0"
)

# CORS Security Configuration - Environment-based
import os

# Load CORS configuration from environment variables
ENV_MODE = os.getenv("NODE_ENV", "development")
CORS_ORIGINS_ENV = os.getenv("CORS_ALLOWED_ORIGINS", "")
CORS_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
CORS_METHODS = os.getenv("CORS_ALLOWED_METHODS", "GET,POST").split(",")
CORS_HEADERS = os.getenv("CORS_ALLOWED_HEADERS", "Content-Type,Authorization").split(",")

# Determine allowed origins based on environment
if CORS_ORIGINS_ENV:
    # Use environment-specified origins
    ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_ENV.split(",")]
elif ENV_MODE == "production":
    # Production: Strict domain-based origins
    ALLOWED_ORIGINS = [
        "https://api.garaksecurity.com",
        "https://dashboard.garaksecurity.com", 
        "https://guardrails.garaksecurity.com",
        "https://docs.garaksecurity.com"
    ]
else:
    # Development: Local and GCP origins
    ALLOWED_ORIGINS = [
        "http://localhost:8501", "http://localhost:8502",
        "http://127.0.0.1:8501", "http://127.0.0.1:8502"
    ]

print(f"🔒 CORS Configuration:")
print(f"   Environment: {ENV_MODE}")
print(f"   Allowed Origins: {ALLOWED_ORIGINS}")
print(f"   Allow Credentials: {CORS_CREDENTIALS}")

# Apply secure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# Pydantic models
class GuardrailToggle(BaseModel):
    guardrail_name: str
    enabled: bool

class GuardrailTest(BaseModel):
    guardrail_name: str
    test_input: str

class ConfigUpdate(BaseModel):
    config: Dict[str, Any]

class ServiceHealth(BaseModel):
    service_name: str
    status: str
    response_time: float
    timestamp: datetime

# Global state
guardrail_states = {}
metrics = {
    "requests_total": 0,
    "blocked_total": 0,
    "allowed_total": 0,
    "service_calls": {},
    "response_times": {}
}

class GuardrailsController:
    def __init__(self):
        self.config_path = CONFIG_PATH
        self.load_current_states()
    
    def load_current_states(self):
        """Load current guardrail states from config."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            rails_config = config.get("rails", {}).get("config", {})
            for guardrail_name, guardrail_config in rails_config.items():
                guardrail_states[guardrail_name] = guardrail_config.get("enabled", True)
                
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Load current configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            return {"error": str(e)}
    
    def toggle_guardrail(self, guardrail_name: str, enabled: bool) -> bool:
        """Toggle a guardrail on/off."""
        config = self.get_config()
        if "error" in config:
            return False
        
        # Ensure rails config structure exists
        if "rails" not in config:
            config["rails"] = {"config": {}}
        if "config" not in config["rails"]:
            config["rails"]["config"] = {}
        
        # Update guardrail state
        if guardrail_name not in config["rails"]["config"]:
            config["rails"]["config"][guardrail_name] = {}
        
        config["rails"]["config"][guardrail_name]["enabled"] = enabled
        
        # Save and update state
        if self.save_config(config):
            guardrail_states[guardrail_name] = enabled
            return True
        return False
    
    def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health of a service."""
        service_url = SERVICES.get(service_name)
        if not service_url:
            return {"status": "unknown", "response_time": 0}
        
        try:
            start_time = time.time()
            response = requests.get(f"{service_url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response_time,
                "status_code": response.status_code,
                "timestamp": datetime.now().isoformat()
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "unhealthy", 
                "response_time": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_guardrail(self, guardrail_name: str, test_input: str) -> Dict[str, Any]:
        """Test a specific guardrail."""
        metrics["requests_total"] += 1
        
        # Map guardrail to service
        service_mapping = {
            "jailbreak_detection": "jailbreak",
            "sensitive_data_detection": "presidio", 
            "content_safety": "content_safety",
            "injection_detection": "main",
            "self_check_input": "main",
            "self_check_output": "main",
            "hallucination_detection": "main"
        }
        
        service_name = service_mapping.get(guardrail_name)
        if not service_name:
            return {"error": "Unknown guardrail"}
        
        service_url = SERVICES[service_name]
        
        try:
            start_time = time.time()
            
            if service_name == "jailbreak":
                response = requests.post(
                    f"{service_url}/heuristics",
                    json={"prompt": test_input},
                    timeout=10
                )
                result = response.json()
                blocked = result.get("is_jailbreak", False)
                
            elif service_name == "presidio":
                response = requests.post(
                    f"{service_url}/analyze", 
                    json={"text": test_input},
                    timeout=10
                )
                result = response.json()
                blocked = result.get("has_sensitive_data", False)
                
            elif service_name == "content_safety":
                response = requests.post(
                    f"{service_url}/check",
                    json={"text": test_input},
                    timeout=10
                )
                result = response.json()
                blocked = not result.get("is_safe", True)
                
            else:
                # Main service - use chat completion with config_id
                response = requests.post(
                    f"{service_url}/v1/chat/completions",
                    json={
                        "messages": [{"role": "user", "content": test_input}],
                        "model": "gpt-3.5-turbo-instruct",
                        "config_id": "comprehensive"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    message = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    blocked = "cannot" in message.lower() or "sorry" in message.lower()
                else:
                    return {"error": f"Service error: {response.status_code}"}
            
            # Update metrics
            response_time = (time.time() - start_time) * 1000
            if blocked:
                metrics["blocked_total"] += 1
            else:
                metrics["allowed_total"] += 1
            
            metrics["response_times"][guardrail_name] = response_time
            metrics["service_calls"][service_name] = metrics["service_calls"].get(service_name, 0) + 1
            
            return {
                "guardrail": guardrail_name,
                "blocked": blocked,
                "response_time": response_time,
                "details": result if 'result' in locals() else {},
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}

controller = GuardrailsController()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "NeMo Guardrails Control API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "guardrails": "/guardrails",
            "services": "/services",
            "config": "/config",
            "test": "/test",
            "metrics": "/metrics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/guardrails")
async def get_guardrails():
    """Get all guardrails and their states."""
    return {
        "guardrails": guardrail_states,
        "total": len(guardrail_states),
        "enabled": sum(1 for enabled in guardrail_states.values() if enabled),
        "disabled": sum(1 for enabled in guardrail_states.values() if not enabled)
    }

@app.post("/guardrails/toggle")
async def toggle_guardrail(toggle_request: GuardrailToggle):
    """Toggle a guardrail on/off."""
    success = controller.toggle_guardrail(
        toggle_request.guardrail_name, 
        toggle_request.enabled
    )
    
    if success:
        return {
            "success": True,
            "guardrail": toggle_request.guardrail_name,
            "enabled": toggle_request.enabled,
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to toggle guardrail")

@app.get("/services")
async def get_services_health():
    """Get health status of all services."""
    health_status = {}
    for service_name in SERVICES.keys():
        health_status[service_name] = controller.check_service_health(service_name)
    
    return {
        "services": health_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/services/{service_name}/health")
async def get_service_health(service_name: str):
    """Get health of specific service."""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    
    health = controller.check_service_health(service_name)
    return health

@app.get("/config")
async def get_config():
    """Get current configuration."""
    config = controller.get_config()
    if "error" in config:
        raise HTTPException(status_code=500, detail=config["error"])
    return config

@app.post("/config")
async def update_config(config_update: ConfigUpdate):
    """Update configuration."""
    success = controller.save_config(config_update.config)
    if success:
        controller.load_current_states()  # Reload states
        return {
            "success": True,
            "message": "Configuration updated",
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to update configuration")

@app.post("/test")
async def test_guardrail(test_request: GuardrailTest):
    """Test a guardrail with specific input."""
    result = controller.test_guardrail(
        test_request.guardrail_name,
        test_request.test_input
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@app.get("/metrics")
async def get_metrics():
    """Get system metrics."""
    return {
        "metrics": metrics,
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/metrics")
async def reset_metrics():
    """Reset all metrics."""
    global metrics
    metrics = {
        "requests_total": 0,
        "blocked_total": 0,
        "allowed_total": 0,
        "service_calls": {},
        "response_times": {}
    }
    return {
        "success": True,
        "message": "Metrics reset",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "control_api:app",
        host="0.0.0.0",
        port=8090,
        reload=True,
        log_level="info"
    )