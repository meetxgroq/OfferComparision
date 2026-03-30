#!/usr/bin/env python3
"""
OfferCompare Pro - Server Launcher

This script allows you to easily switch between the real API server (with Gemini)
and the mock API server for development.

Usage:
  python scripts/start_server.py --real     # Start real API server with Gemini
  python scripts/start_server.py --mock     # Start mock API server
  python scripts/start_server.py            # Auto-detect based on API quota
"""

import argparse
import subprocess
import sys
import requests
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent

def check_gemini_quota():
    """Check if Gemini API is available and within quota."""
    try:
        # Quick test to see if Gemini API is working
        from utils.call_llm import call_llm
        result = call_llm("Hello", max_tokens=5)
        return True
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            print("⚠️  Gemini API quota exceeded")
            return False
        elif "api_key" in str(e).lower():
            print("⚠️  Gemini API key not configured")
            return False
        else:
            print(f"⚠️  Gemini API error: {e}")
            return False

def start_real_server():
    """Start the real API server with PocketFlow and Gemini."""
    print("🚀 Starting real API server with Gemini...")
    print("📍 Server will be available at: http://localhost:8001")
    print("📊 Using PocketFlow with async processing")
    print("🤖 AI Provider: Google Gemini")
    print("")
    
    # Load environment variables
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
    
    # Start the real server
    subprocess.run([sys.executable, str(PROJECT_DIR / "api_server.py")])

def start_mock_server():
    """Start the mock API server for development."""
    print("🚀 Starting mock API server...")
    print("📍 Server will be available at: http://localhost:8001")
    print("🎭 Using mock data for development")
    print("⚡ Fast responses without API calls")
    print("")
    subprocess.run([sys.executable, str(SCRIPT_DIR / "mock_api_server.py")])

def main():
    parser = argparse.ArgumentParser(description="Start OfferCompare Pro API server")
    parser.add_argument("--real", action="store_true", help="Force start real API server")
    parser.add_argument("--mock", action="store_true", help="Force start mock API server")
    
    args = parser.parse_args()
    
    if args.real and args.mock:
        print("❌ Cannot specify both --real and --mock")
        sys.exit(1)
    
    if args.real:
        start_real_server()
    elif args.mock:
        start_mock_server()
    else:
        # Auto-detect based on Gemini availability
        print("🔍 Auto-detecting best server option...")
        
        if check_gemini_quota():
            print("✅ Gemini API available - starting real server")
            start_real_server()
        else:
            print("🎭 Falling back to mock server")
            start_mock_server()

if __name__ == "__main__":
    main()
