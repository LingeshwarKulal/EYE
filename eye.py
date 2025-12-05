#!/usr/bin/env python3
"""
EYE - Automated Attack Surface Manager
Launcher script for cleaner command-line usage

Usage:
    python eye.py -d example.com
    OR
    ./eye.py -d example.com (Linux/Mac with chmod +x eye.py)
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from main import run
    run()
