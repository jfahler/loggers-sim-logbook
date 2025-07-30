#!/usr/bin/env python3
"""
Test script for DCS Server Bot REST API integration

This script tests all the REST API endpoints to ensure they work correctly
with the Loggers DCS Squadron Logbook backend.
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration
LOGGERS_BASE_URL = "http://localhost:5000"
DCS_REST_API_TOKEN = "loggers_rest_api_token_2024"
TEST_TIMEOUT = 10

def make_request(method, endpoint, data=None, headers=None):
    """Make HTTP request to Loggers backend"""
    url = f"{LOGGERS_BASE_URL}{endpoint}"
    
    if headers is None:
        headers = {}
    
    if DCS_REST_API_TOKEN:
        headers['Authorization'] = f'Bearer {DCS_REST_API_TOKEN}'
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=TEST_TIMEOUT)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=TEST_TIMEOUT)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
        
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def test_endpoint(name, method, endpoint, data=None, expected_status=200):
    """Test a specific endpoint"""
    print(f"\n🧪 Testing {name}...")
    print(f"   {method} {endpoint}")
    
    response = make_request(method, endpoint, data)
    
    if response is None:
        print(f"❌ {name}: Request failed")
        return False
    
    if response.status_code == expected_status:
        print(f"✅ {name}: Success (Status: {response.status_code})")
        
        try:
            result = response.json()
            if 'request_id' in result:
                print(f"   Request ID: {result['request_id']}")
            
            # Print relevant data for different endpoints
            if 'server' in result:
                server = result['server']
                print(f"   Server: {server.get('name', 'N/A')}")
                print(f"   Mission: {server.get('mission_name', 'N/A')}")
                print(f"   Players: {server.get('players_count', 0)}/{server.get('max_players', 0)}")
            
            elif 'players' in result:
                players = result['players']
                print(f"   Players: {len(players)}")
                for player in players[:3]:  # Show first 3 players
                    print(f"     - {player.get('name', 'N/A')} ({player.get('unit_type', 'N/A')})")
                if len(players) > 3:
                    print(f"     ... and {len(players) - 3} more")
            
            elif 'mission' in result:
                mission = result['mission']
                print(f"   Mission: {mission.get('name', 'N/A')}")
                print(f"   Theatre: {mission.get('theatre', 'N/A')}")
                print(f"   Duration: {mission.get('duration', 0)} seconds")
            
            elif 'missions' in result:
                missions = result['missions']
                print(f"   Available missions: {len(missions)}")
                for mission in missions[:3]:  # Show first 3 missions
                    print(f"     - {mission}")
                if len(missions) > 3:
                    print(f"     ... and {len(missions) - 3} more")
            
            elif 'stats' in result:
                stats = result['stats']
                print(f"   Server stats retrieved successfully")
                print(f"   Keys: {', '.join(stats.keys())}")
            
            elif 'message' in result:
                print(f"   Message: {result['message']}")
            
        except json.JSONDecodeError:
            print(f"   Response: {response.text[:200]}...")
        
        return True
    
    else:
        print(f"❌ {name}: Failed (Status: {response.status_code})")
        try:
            error_data = response.json()
            if 'error' in error_data:
                error = error_data['error']
                print(f"   Error: {error.get('message', 'Unknown error')}")
                print(f"   Code: {error.get('code', 'N/A')}")
        except json.JSONDecodeError:
            print(f"   Response: {response.text[:200]}...")
        
        return False

def test_health_check():
    """Test the health check endpoint"""
    print("\n🏥 Testing Health Check...")
    
    response = make_request('GET', '/health')
    
    if response is None:
        print("❌ Health check: Request failed")
        return False
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"✅ Health check: Success")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   DCS Bot Enabled: {data.get('dcs_bot_enabled', 'N/A')}")
            print(f"   DCS REST API Enabled: {data.get('dcs_rest_api_enabled', 'N/A')}")
            return True
        except json.JSONDecodeError:
            print(f"❌ Health check: Invalid JSON response")
            return False
    else:
        print(f"❌ Health check: Failed (Status: {response.status_code})")
        return False

def main():
    """Main test function"""
    print("🚀 DCS Server Bot REST API Integration Test")
    print("=" * 50)
    print(f"Target URL: {LOGGERS_BASE_URL}")
    print(f"Token: {DCS_REST_API_TOKEN[:10]}..." if DCS_REST_API_TOKEN else "Token: None")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test health check first
    if not test_health_check():
        print("\n❌ Health check failed. Make sure the Loggers backend is running.")
        return
    
    # Test all REST API endpoints
    tests = [
        ("Server Information", "GET", "/dcs/server/info"),
        ("Server Players", "GET", "/dcs/server/players"),
        ("Mission Information", "GET", "/dcs/server/mission"),
        ("Available Missions", "GET", "/dcs/server/missions"),
        ("Server Statistics", "GET", "/dcs/server/stats"),
        ("Send Chat Message", "POST", "/dcs/server/chat", {
            "message": f"Test message from Loggers at {datetime.now().isoformat()}",
            "coalition": "all"
        }),
        ("Restart Mission", "POST", "/dcs/server/mission/restart"),
    ]
    
    # Test player info endpoint if we have players
    print("\n🔍 Checking for players to test player info endpoint...")
    response = make_request('GET', '/dcs/server/players')
    if response and response.status_code == 200:
        try:
            data = response.json()
            players = data.get('players', [])
            if players:
                player_id = players[0].get('id', players[0].get('ucid', 'test'))
                tests.append(("Player Information", "GET", f"/dcs/server/players/{player_id}"))
                print(f"   Found player: {players[0].get('name', 'Unknown')} (ID: {player_id})")
            else:
                print("   No players found, skipping player info test")
        except json.JSONDecodeError:
            print("   Could not parse players response")
    
    # Run all tests
    passed = 0
    total = len(tests)
    
    for test in tests:
        if len(test) == 4:
            name, method, endpoint, data = test
            if test_endpoint(name, method, endpoint, data):
                passed += 1
        else:
            name, method, endpoint = test
            if test_endpoint(name, method, endpoint):
                passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! DCS REST API integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the configuration and DCS Server Bot status.")
    
    # Additional information
    print("\n💡 Tips:")
    print("- Make sure DCSServerBot is running with REST API plugin enabled")
    print("- Verify the REST API token matches in both configurations")
    print("- Check that the REST API is accessible on the configured port")
    print("- Review the logs for detailed error information")

if __name__ == "__main__":
    main() 