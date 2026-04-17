"""
Startup validation to ensure required environment and dependencies are available
"""
import os
import sys

def validate_env():
    """Validate that required environment variables are set"""
    warnings = []
    
    # Optional but recommended variables
    optional_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    
    for key in optional_vars:
        if not os.getenv(key):
            warnings.append(f"Optional env variable not set: {key}")
    
    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}")
    
    # Required variables
    required_vars = ["API_SECRET"]
    
    for key in required_vars:
        if not os.getenv(key):
            raise RuntimeError(f"Missing required env variable: {key}")
    
    print("Environment validation passed")

def validate_dependencies():
    """Validate that critical dependencies are available"""
    try:
        import fastapi
        print("FastAPI available")
    except ImportError:
        raise RuntimeError("FastAPI is required but not installed")
    
    try:
        import uvicorn
        print("Uvicorn available")
    except ImportError:
        raise RuntimeError("Uvicorn is required but not installed")
