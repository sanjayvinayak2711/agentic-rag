#!/usr/bin/env python3
"""
Simple startup script for Agentic-RAG Application
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleOutputCP(65001)  # UTF-8
    kernel32.SetConsoleCP(65001)
    # Also reconfigure stdout/stderr
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["data/uploads", "data/chroma_db", "data/cache", "logs"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("✅ Directories created")

def check_environment():
    """Check environment configuration - runtime config only"""
    print("✅ Using runtime configuration (no .env file needed)")

def start_backend():
    """Start the backend server"""
    print("🚀 Starting backend server...")
    os.chdir("backend")
    
    try:
        # Start the server in a subprocess
        process = subprocess.Popen([sys.executable, "main.py"])
        
        # Wait a moment for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Open browser automatically
        print("🌐 Opening browser...")
        webbrowser.open("http://localhost:8000")
        
        print("✅ Browser opened at http://localhost:8000")
        print("📚 API docs available at http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop the server\n")
        
        # Wait for the process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🎯 Agentic-RAG Application Startup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    if not check_dependencies():
        if not install_dependencies():
            sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check environment
    check_environment()
    
    print("\n🌐 Application will be available at: http://localhost:8000")
    print("📚 API documentation: http://localhost:8000/docs")
    print("🔄 Browser will open automatically...")
    
    # Start backend
    start_backend()

if __name__ == "__main__":
    main()
