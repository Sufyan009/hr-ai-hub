#!/usr/bin/env python3
"""
Simple Qdrant Server Starter
This script starts a local Qdrant server for development purposes.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_qdrant_installed():
    """Check if Qdrant is available as a command"""
    try:
        result = subprocess.run(['qdrant', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def start_qdrant_server():
    """Start Qdrant server using available methods"""
    
    print("🚀 Starting Qdrant Server...")
    print("=" * 50)
    
    # Method 1: Try using qdrant command if available
    if check_qdrant_installed():
        print("✅ Found Qdrant binary, starting server...")
        try:
            subprocess.run(['qdrant'], check=True)
        except KeyboardInterrupt:
            print("\n🛑 Qdrant server stopped by user")
        except Exception as e:
            print(f"❌ Error starting Qdrant: {e}")
            return False
        return True
    
    # Method 2: Try Docker if available
    print("🔍 Trying Docker method...")
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Docker found, starting Qdrant container...")
            try:
                subprocess.run([
                    'docker', 'run', '-d', 
                    '-p', '6333:6333', 
                    '-p', '6334:6334',
                    '--name', 'qdrant-server',
                    'qdrant/qdrant'
                ], check=True)
                print("✅ Qdrant container started successfully!")
                print("🌐 Qdrant server running at: http://localhost:6333")
                print("📊 Dashboard available at: http://localhost:6333/dashboard")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Docker error: {e}")
                return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Docker not available")
    
    # Method 3: Manual installation instructions
    print("\n📋 Manual Installation Options:")
    print("1. Install Docker Desktop and run:")
    print("   docker run -d -p 6333:6333 -p 6334:6334 --name qdrant qdrant/qdrant")
    print("\n2. Download Qdrant binary from:")
    print("   https://github.com/qdrant/qdrant/releases")
    print("   Then run: qdrant")
    print("\n3. Use cloud Qdrant service:")
    print("   Update your .env file with cloud Qdrant URL")
    
    return False

def test_qdrant_connection():
    """Test if Qdrant server is responding"""
    try:
        response = requests.get("http://localhost:6333/collections", timeout=5)
        if response.status_code == 200:
            print("✅ Qdrant server is responding!")
            return True
        else:
            print(f"❌ Qdrant server responded with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Qdrant server: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Qdrant Server Setup")
    print("=" * 50)
    
    # Check if Qdrant is already running
    if test_qdrant_connection():
        print("✅ Qdrant server is already running!")
        sys.exit(0)
    
    # Try to start Qdrant
    if start_qdrant_server():
        print("\n✅ Qdrant server started successfully!")
        print("🌐 Server URL: http://localhost:6333")
        print("📊 Dashboard: http://localhost:6333/dashboard")
        print("\n💡 To stop the server, press Ctrl+C")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Qdrant server stopped")
    else:
        print("\n❌ Failed to start Qdrant server")
        print("Please follow the manual installation instructions above")
        sys.exit(1) 