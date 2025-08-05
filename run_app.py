#!/usr/bin/env python3
"""
Launcher script for the Speech-to-Code AI Streamlit application.
This script checks dependencies and launches the app with proper error handling.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'whisper',
        'torch',
        'fuzzywuzzy',
        'plotly',
        'librosa'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages using:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_data_files():
    """Check if required data files exist"""
    required_files = ['ICD-10.csv', 'CPT.csv']
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file} - Missing")
    
    if missing_files:
        print(f"\n❌ Missing data files: {', '.join(missing_files)}")
        print("Please ensure all required CSV files are in the project directory.")
        return False
    
    return True

def check_secrets():
    """Check if secrets file exists"""
    secrets_file = Path('.streamlit/secrets.toml')
    
    if secrets_file.exists():
        print("✅ .streamlit/secrets.toml")
        return True
    else:
        print("⚠️  .streamlit/secrets.toml - Missing")
        print("Note: Hugging Face token is optional but recommended for speaker diarization")
        return True  # Not critical for basic functionality

def main():
    """Main launcher function"""
    print("🏥 Speech-to-Code AI - Application Launcher")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    print("\n📁 Checking data files...")
    if not check_data_files():
        sys.exit(1)
    
    print("\n🔐 Checking configuration...")
    check_secrets()
    
    print("\n🚀 Starting Streamlit application...")
    print("The app will open in your default browser at http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Launch Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error launching application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 