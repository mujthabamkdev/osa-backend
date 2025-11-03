#!/usr/bin/env python3
"""Test if the app can be imported"""
import sys
sys.path.insert(0, '/Users/mujthabamk/Desktop/real-world-projects/osa/OSA/osa-backend')

try:
    from app.main import app
    print("✓ App imported successfully")
    print(f"✓ App: {app}")
    print(f"✓ Routes: {[route.path for route in app.routes[:5]]}")
except Exception as e:
    print(f"❌ Error importing app: {e}")
    import traceback
    traceback.print_exc()
