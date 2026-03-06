#!/usr/bin/env python3
"""
Ultra-Fast Startup for Agentic RAG Project
"""

import os
import sys
import subprocess
import webbrowser
import time

def check_requirements():
    """Quick check if all required files exist"""
    required_files = [
        'app/main.py', 
        'ui/index.html', 
        'ui/main.js', 
        'ui/styles.css'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Missing: {file}")
            return False
    
    return True

def start_backend():
    """Start backend server instantly"""
    print("🚀 Starting backend...")
    try:
        # Use Popen for instant start (no waiting)
        backend_process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 
            'app.main:app', 
            '--host', '0.0.0.0', 
            '--port', '8000'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✅ Backend started instantly!")
        return backend_process
            
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return None

def open_frontend():
    """Open frontend instantly"""
    try:
        webbrowser.open('http://localhost:8000')
        print("✅ Frontend opened!")
        return True
    except Exception as e:
        print(f"❌ Browser error: {e}")
        return False

def main():
    """Ultra-fast startup"""
    print("⚡ Agentic RAG - Ultra Fast Startup")
    print("=" * 40)
    
    # Quick check
    if not check_requirements():
        print("❌ Missing files!")
        return
    
    # Start backend instantly
    backend_process = start_backend()
    if not backend_process:
        return
    
    # Open frontend instantly  
    open_frontend()
    
    print("=" * 40)
    print("🎉 READY INSTANTLY!")
    print("📝 Frontend: http://localhost:8000")
    print("⚡ Backend: Running in background")
    print("=" * 40)
    
    # Keep running but don't block
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        backend_process.terminate()
        print("✅ Stopped")

if __name__ == "__main__":
    main()
