#!/usr/bin/env python3
"""
NeMo Guardrails Monitoring and Control Dashboard
Provides real-time monitoring and dynamic control of guardrail services
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
import os

# Configuration
SERVICES = {
    "main": {"url": "http://localhost:8000", "name": "Main NeMo Guardrails"},
    "jailbreak": {"url": "http://localhost:1337", "name": "Jailbreak Detection"},
    "presidio": {"url": "http://localhost:5001", "name": "Sensitive Data Detection"},
    "content_safety": {"url": "http://localhost:5002", "name": "Content Safety"}
}

CONTROL_API_URL = "http://localhost:8090"

GUARDRAIL_CATEGORIES = {
    "jailbreak_detection": {
        "name": "Jailbreak Detection",
        "description": "Detects prompt injection attacks",
        "service": "jailbreak",
        "enabled": True
    },
    "injection_detection": {
        "name": "Injection Detection", 
        "description": "Detects code, SQL, XSS injections",
        "service": "main",
        "enabled": True
    },
    "sensitive_data_detection": {
        "name": "Sensitive Data Detection",
        "description": "Detects and anonymizes PII",
        "service": "presidio", 
        "enabled": True
    },
    "content_safety": {
        "name": "Content Safety",
        "description": "Content safety validation",
        "service": "content_safety",
        "enabled": True
    },
    "self_check_input": {
        "name": "Self Check Input",
        "description": "LLM-based input validation",
        "service": "main",
        "enabled": True
    },
    "self_check_output": {
        "name": "Self Check Output", 
        "description": "LLM-based output validation",
        "service": "main",
        "enabled": True
    },
    "hallucination_detection": {
        "name": "Hallucination Detection",
        "description": "Detects AI hallucinations",
        "service": "main",
        "enabled": True
    }
}

class GuardrailsMonitor:
    def __init__(self):
        self.config_path = "/Users/divyachitimalla/NeMo-Guardrails/comprehensive-config/config.yml"
        self.logs_path = "/Users/divyachitimalla/NeMo-Guardrails/logs"
        self.metrics = {"requests": 0, "blocked": 0, "allowed": 0}
        
    def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health of a service."""
        service_info = SERVICES.get(service_name)
        if not service_info:
            return {"status": "unknown", "response_time": 0}
            
        try:
            start_time = time.time()
            response = requests.get(f"{service_info['url']}/health", timeout=5)
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response_time * 1000,  # Convert to ms
                "status_code": response.status_code
            }
        except requests.exceptions.RequestException:
            return {"status": "unhealthy", "response_time": 0, "status_code": 0}
    
    def get_all_service_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all services."""
        try:
            # Get health from control API
            response = requests.get(f"{CONTROL_API_URL}/services", timeout=10)
            if response.status_code == 200:
                api_health = response.json()["services"]
                # Add service names
                for service_name, health in api_health.items():
                    health["name"] = SERVICES.get(service_name, {}).get("name", service_name)
                return api_health
        except:
            pass
        
        # Fallback to direct health checks
        health_status = {}
        for service_name, service_info in SERVICES.items():
            health_status[service_name] = self.check_service_health(service_name)
            health_status[service_name]["name"] = service_info["name"]
        return health_status
    
    def test_guardrail(self, guardrail_name: str, test_input: str) -> Dict[str, Any]:
        """Test a specific guardrail with input."""
        try:
            # Use Control API to test guardrail
            response = requests.post(
                f"{CONTROL_API_URL}/test",
                json={"guardrail_name": guardrail_name, "test_input": test_input},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def load_config(self) -> Dict[str, Any]:
        """Load current configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            return {"error": str(e)}
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            return True
        except Exception as e:
            st.error(f"Failed to save config: {e}")
            return False
    
    def toggle_guardrail(self, guardrail_name: str, enabled: bool) -> bool:
        """Enable or disable a guardrail."""
        try:
            # Use Control API to toggle guardrail
            response = requests.post(
                f"{CONTROL_API_URL}/guardrails/toggle",
                json={"guardrail_name": guardrail_name, "enabled": enabled},
                timeout=10
            )
            return response.status_code == 200
        except:
            # Fallback to direct config modification
            config = self.load_config()
            if "error" in config:
                return False
                
            # Update the configuration
            if "rails" not in config:
                config["rails"] = {"config": {}}
            if "config" not in config["rails"]:
                config["rails"]["config"] = {}
                
            # Set the guardrail status
            if guardrail_name in config["rails"]["config"]:
                config["rails"]["config"][guardrail_name]["enabled"] = enabled
            else:
                config["rails"]["config"][guardrail_name] = {"enabled": enabled}
                
            return self.save_config(config)

def main():
    st.set_page_config(
        page_title="NeMo Guardrails Monitor",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    monitor = GuardrailsMonitor()
    
    # Header
    st.title("🛡️ NeMo Guardrails Monitoring Dashboard")
    st.markdown("**Real-time monitoring and control of all guardrail categories**")
    
    # Sidebar for controls
    st.sidebar.header("🎛️ Guardrail Controls")
    
    # Service Health Section
    st.header("📊 Service Health Status")
    
    health_status = monitor.get_all_service_health()
    
    # Create service health metrics
    health_cols = st.columns(len(SERVICES))
    for i, (service_name, health) in enumerate(health_status.items()):
        with health_cols[i]:
            status_color = "🟢" if health["status"] == "healthy" else "🔴"
            st.metric(
                label=f"{status_color} {health['name']}",
                value=health["status"].title(),
                delta=f"{health['response_time']:.0f}ms" if health["response_time"] > 0 else "N/A"
            )
    
    # Guardrail Control Section
    st.header("🔧 Guardrail Configuration")
    
    # Create tabs for different categories
    input_tab, output_tab, testing_tab, config_tab = st.tabs([
        "Input Protection", "Output Validation", "Testing", "Configuration"
    ])
    
    with input_tab:
        st.subheader("Input Protection Rails")
        
        input_guardrails = [
            "jailbreak_detection", "injection_detection", 
            "sensitive_data_detection", "content_safety", "self_check_input"
        ]
        
        for guardrail_name in input_guardrails:
            guardrail_info = GUARDRAIL_CATEGORIES[guardrail_name]
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{guardrail_info['name']}**")
                st.write(f"_{guardrail_info['description']}_")
            
            with col2:
                service_health = health_status.get(guardrail_info['service'], {})
                status_icon = "🟢" if service_health.get("status") == "healthy" else "🔴"
                st.write(f"Service: {status_icon}")
            
            with col3:
                enabled = st.toggle(
                    "Enabled",
                    value=guardrail_info['enabled'],
                    key=f"toggle_{guardrail_name}"
                )
                if enabled != guardrail_info['enabled']:
                    if monitor.toggle_guardrail(guardrail_name, enabled):
                        GUARDRAIL_CATEGORIES[guardrail_name]['enabled'] = enabled
                        st.success(f"{'Enabled' if enabled else 'Disabled'} {guardrail_info['name']}")
                    else:
                        st.error("Failed to update configuration")
    
    with output_tab:
        st.subheader("Output Validation Rails")
        
        output_guardrails = [
            "self_check_output", "hallucination_detection"
        ]
        
        for guardrail_name in output_guardrails:
            guardrail_info = GUARDRAIL_CATEGORIES[guardrail_name]
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{guardrail_info['name']}**")
                st.write(f"_{guardrail_info['description']}_")
            
            with col2:
                service_health = health_status.get(guardrail_info['service'], {})
                status_icon = "🟢" if service_health.get("status") == "healthy" else "🔴"
                st.write(f"Service: {status_icon}")
            
            with col3:
                enabled = st.toggle(
                    "Enabled",
                    value=guardrail_info['enabled'],
                    key=f"toggle_{guardrail_name}"
                )
                if enabled != guardrail_info['enabled']:
                    if monitor.toggle_guardrail(guardrail_name, enabled):
                        GUARDRAIL_CATEGORIES[guardrail_name]['enabled'] = enabled
                        st.success(f"{'Enabled' if enabled else 'Disabled'} {guardrail_info['name']}")
                    else:
                        st.error("Failed to update configuration")
    
    with testing_tab:
        st.subheader("🧪 Guardrail Testing")
        
        # Test input
        test_input = st.text_area(
            "Enter test input:",
            value="Hello, how can you help me?",
            height=100
        )
        
        # Select guardrail to test
        selected_guardrail = st.selectbox(
            "Select guardrail to test:",
            options=list(GUARDRAIL_CATEGORIES.keys()),
            format_func=lambda x: GUARDRAIL_CATEGORIES[x]['name']
        )
        
        if st.button("🚀 Test Guardrail"):
            if test_input:
                with st.spinner(f"Testing {GUARDRAIL_CATEGORIES[selected_guardrail]['name']}..."):
                    result = monitor.test_guardrail(selected_guardrail, test_input)
                    
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        # Display results
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            blocked = result.get("blocked", False)
                            status_color = "🔴" if blocked else "🟢"
                            st.metric(
                                "Result",
                                f"{status_color} {'BLOCKED' if blocked else 'ALLOWED'}"
                            )
                        
                        with col2:
                            if "confidence" in result:
                                st.metric("Confidence", f"{result['confidence']:.2f}")
                            elif "entities" in result:
                                st.metric("Entities Found", len(result['entities']))
                            elif "categories" in result:
                                st.metric("Violations", len(result['categories']))
                        
                        # Show details
                        st.subheader("Details")
                        st.json(result["details"])
            else:
                st.warning("Please enter test input")
    
    with config_tab:
        st.subheader("⚙️ Configuration Management")
        
        # Current configuration
        config = monitor.load_config()
        if "error" not in config:
            st.subheader("Current Configuration")
            st.code(yaml.dump(config, default_flow_style=False), language='yaml')
            
            # Configuration editor
            st.subheader("Edit Configuration")
            edited_config = st.text_area(
                "YAML Configuration:",
                value=yaml.dump(config, default_flow_style=False),
                height=400
            )
            
            if st.button("💾 Save Configuration"):
                try:
                    new_config = yaml.safe_load(edited_config)
                    if monitor.save_config(new_config):
                        st.success("Configuration saved successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to save configuration")
                except yaml.YAMLError as e:
                    st.error(f"Invalid YAML: {e}")
        else:
            st.error(f"Could not load configuration: {config['error']}")
    
    # Real-time metrics (bottom section)
    st.header("📈 Real-time Metrics")
    
    # Metrics placeholder for future implementation
    metrics_cols = st.columns(4)
    
    with metrics_cols[0]:
        st.metric("Total Requests", monitor.metrics["requests"])
    
    with metrics_cols[1]:
        st.metric("Blocked Requests", monitor.metrics["blocked"])
    
    with metrics_cols[2]:
        st.metric("Allowed Requests", monitor.metrics["allowed"])
    
    with metrics_cols[3]:
        block_rate = (monitor.metrics["blocked"] / max(monitor.metrics["requests"], 1)) * 100
        st.metric("Block Rate", f"{block_rate:.1f}%")
    
    # Auto-refresh
    if st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=False):
        time.sleep(30)
        st.experimental_rerun()
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now"):
        st.experimental_rerun()

if __name__ == "__main__":
    main()