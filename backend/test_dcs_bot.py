#!/usr/bin/env python3
"""
Test script for DCS Server Bot integration

This script tests the USERSTATS and MISSIONSTATS webhook endpoints
with sample data that mimics what DCSServerBot would send.
"""

import json
import requests
import time
from datetime import datetime, timezone

# Configuration
BASE_URL = "http://localhost:5000"
TEST_ENABLED = True

def test_userstats_webhook():
    """Test USERSTATS webhook endpoint"""
    print("🧪 Testing USERSTATS webhook...")
    
    # Sample USERSTATS data based on DCSServerBot format
    userstats_data = {
        "player_name": "TestPilot",
        "player_ucid": "test_ucid_12345",
        "player_id": 12345,
        "server_name": "Test DCS Server",
        "mission_name": "Operation Test Mission",
        "mission_id": "test_mission_001",
        "flight_time": 3600,  # 1 hour in seconds
        "kills": {
            "air": 2,
            "ground": 3,
            "friendly": 0
        },
        "deaths": 1,
        "ejections": 0,
        "crashes": 0,
        "aircraft_type": "F-16C",
        "side": "blue",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/dcs/userstats",
            json=userstats_data,
            headers={
                "Content-Type": "application/json",
                "X-DCS-Signature": "test_signature"
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ USERSTATS webhook test passed!")
            return True
        else:
            print("❌ USERSTATS webhook test failed!")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ USERSTATS webhook test failed with error: {e}")
        return False

def test_missionstats_webhook():
    """Test MISSIONSTATS webhook endpoint"""
    print("\n🧪 Testing MISSIONSTATS webhook...")
    
    # Sample MISSIONSTATS data based on DCSServerBot format
    missionstats_data = {
        "mission_name": "Operation Test Mission",
        "mission_id": "test_mission_001",
        "server_name": "Test DCS Server",
        "start_time": datetime.now(timezone.utc).isoformat(),
        "end_time": datetime.now(timezone.utc).isoformat(),
        "duration": 7200,  # 2 hours in seconds
        "players": [
            {
                "name": "TestPilot1",
                "ucid": "test_ucid_1",
                "flight_time": 3600,
                "kills": {"air": 2, "ground": 1},
                "deaths": 1,
                "ejections": 0,
                "aircraft": "F-16C"
            },
            {
                "name": "TestPilot2",
                "ucid": "test_ucid_2",
                "flight_time": 1800,
                "kills": {"air": 1, "ground": 2},
                "deaths": 0,
                "ejections": 0,
                "aircraft": "F/A-18C"
            }
        ],
        "statistics": {
            "total_kills": 6,
            "total_deaths": 1,
            "total_flight_time": 5400,
            "aircraft_used": ["F-16C", "F/A-18C"]
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/dcs/missionstats",
            json=missionstats_data,
            headers={
                "Content-Type": "application/json",
                "X-DCS-Signature": "test_signature"
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ MISSIONSTATS webhook test passed!")
            return True
        else:
            print("❌ MISSIONSTATS webhook test failed!")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ MISSIONSTATS webhook test failed with error: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint to check DCS Bot status"""
    print("\n🏥 Testing health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"Health Status: {health_data}")
            
            dcs_bot_enabled = health_data.get("dcs_bot_enabled", False)
            dcs_bot_configured = health_data.get("dcs_bot_webhook_configured", False)
            
            print(f"DCS Bot Enabled: {dcs_bot_enabled}")
            print(f"DCS Bot Webhook Configured: {dcs_bot_configured}")
            
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed with error: {e}")
        return False

def test_invalid_data():
    """Test webhook endpoints with invalid data"""
    print("\n🧪 Testing invalid data handling...")
    
    # Test USERSTATS with missing required fields
    invalid_userstats = {
        "player_name": "TestPilot"
        # Missing required fields
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/dcs/userstats",
            json=invalid_userstats,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Invalid USERSTATS Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Invalid USERSTATS data properly rejected!")
        else:
            print("❌ Invalid USERSTATS data not properly rejected!")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Invalid USERSTATS test failed: {e}")
    
    # Test MISSIONSTATS with missing required fields
    invalid_missionstats = {
        "mission_name": "Test Mission"
        # Missing required fields
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/dcs/missionstats",
            json=invalid_missionstats,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Invalid MISSIONSTATS Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Invalid MISSIONSTATS data properly rejected!")
        else:
            print("❌ Invalid MISSIONSTATS data not properly rejected!")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Invalid MISSIONSTATS test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting DCS Server Bot Integration Tests")
    print("=" * 50)
    
    if not TEST_ENABLED:
        print("❌ Tests are disabled. Set TEST_ENABLED = True to run tests.")
        return
    
    # Test health endpoint first
    health_ok = test_health_endpoint()
    
    if not health_ok:
        print("❌ Health check failed. Make sure the server is running.")
        return
    
    # Test valid webhook data
    userstats_ok = test_userstats_webhook()
    missionstats_ok = test_missionstats_webhook()
    
    # Test invalid data handling
    test_invalid_data()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"USERSTATS Webhook: {'✅ PASS' if userstats_ok else '❌ FAIL'}")
    print(f"MISSIONSTATS Webhook: {'✅ PASS' if missionstats_ok else '❌ FAIL'}")
    
    if all([health_ok, userstats_ok, missionstats_ok]):
        print("\n🎉 All tests passed! DCS Server Bot integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the server logs for details.")

if __name__ == "__main__":
    main() 