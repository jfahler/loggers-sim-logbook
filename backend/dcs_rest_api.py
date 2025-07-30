"""
DCS Server Bot REST API Integration Module

This module provides integration with DCSServerBot's REST API plugin,
offering additional commands and endpoints for server management,
player information, and mission control.

Based on DCSServerBot REST API documentation:
https://github.com/Special-K-s-Flightsim-Bots/DCSServerBot/tree/master/plugins/restapi
"""

import os
import json
import logging
import requests
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from urllib.parse import urljoin

from validation import sanitize_string, ValidationError
from error_handling import APIError, ErrorCodes, log_operation_start, log_operation_success, log_operation_failure

logger = logging.getLogger(__name__)

# Configuration
DCS_REST_API_ENABLED = os.getenv("DCS_REST_API_ENABLED", "false").lower() == "true"
DCS_REST_API_URL = os.getenv("DCS_REST_API_URL", "http://localhost:8080")
DCS_REST_API_TOKEN = os.getenv("DCS_REST_API_TOKEN", "")
DCS_REST_API_TIMEOUT = int(os.getenv("DCS_REST_API_TIMEOUT", "30"))

@dataclass
class DCSPlayer:
    """Data structure for DCS player information"""
    name: str
    ucid: str
    id: int
    side: str
    slot: str
    unit_type: str
    unit_name: str
    group_id: int
    ping: int
    connected_at: datetime

@dataclass
class DCSServer:
    """Data structure for DCS server information"""
    name: str
    mission_name: str
    mission_start_time: datetime
    players_count: int
    max_players: int
    status: str
    version: str

@dataclass
class DCSMission:
    """Data structure for DCS mission information"""
    name: str
    description: str
    theatre: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: int
    weather: Dict[str, Any]
    briefing: str

class DCSRestAPI:
    """DCS Server Bot REST API client"""
    
    def __init__(self, base_url: str = None, token: str = None, timeout: int = None):
        self.base_url = base_url or DCS_REST_API_URL
        self.token = token or DCS_REST_API_TOKEN
        self.timeout = timeout or DCS_REST_API_TIMEOUT
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            })
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to DCS REST API"""
        url = urljoin(self.base_url, endpoint)
        
        try:
            log_operation_start("dcs_rest_api_request", {
                "method": method,
                "endpoint": endpoint,
                "url": url
            })
            
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            log_operation_success("dcs_rest_api_request", {
                "method": method,
                "endpoint": endpoint,
                "status_code": response.status_code
            })
            
            return result
            
        except requests.exceptions.RequestException as e:
            log_operation_failure("dcs_rest_api_request", e)
            raise APIError(
                error_code=ErrorCodes.DCS_REST_API_ERROR,
                message=f"DCS REST API request failed: {str(e)}",
                status_code=500
            )
    
    def get_server_info(self) -> DCSServer:
        """Get current server information"""
        try:
            data = self._make_request('GET', '/server/info')
            
            # Parse mission start time
            start_time_str = data.get('mission_start_time', '')
            if start_time_str:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            else:
                start_time = datetime.now(timezone.utc)
            
            return DCSServer(
                name=sanitize_string(data.get('name', ''), max_length=100),
                mission_name=sanitize_string(data.get('mission_name', ''), max_length=200),
                mission_start_time=start_time,
                players_count=int(data.get('players_count', 0)),
                max_players=int(data.get('max_players', 0)),
                status=sanitize_string(data.get('status', ''), max_length=50),
                version=sanitize_string(data.get('version', ''), max_length=50)
            )
        except (ValueError, KeyError) as e:
            raise ValidationError(f"Invalid server info data: {str(e)}")
    
    def get_players(self) -> List[DCSPlayer]:
        """Get current players on server"""
        try:
            data = self._make_request('GET', '/server/players')
            players = []
            
            for player_data in data.get('players', []):
                # Parse connected time
                connected_str = player_data.get('connected_at', '')
                if connected_str:
                    connected_at = datetime.fromisoformat(connected_str.replace('Z', '+00:00'))
                else:
                    connected_at = datetime.now(timezone.utc)
                
                player = DCSPlayer(
                    name=sanitize_string(player_data.get('name', ''), max_length=100),
                    ucid=sanitize_string(player_data.get('ucid', ''), max_length=50),
                    id=int(player_data.get('id', 0)),
                    side=sanitize_string(player_data.get('side', ''), max_length=10),
                    slot=sanitize_string(player_data.get('slot', ''), max_length=100),
                    unit_type=sanitize_string(player_data.get('unit_type', ''), max_length=50),
                    unit_name=sanitize_string(player_data.get('unit_name', ''), max_length=100),
                    group_id=int(player_data.get('group_id', 0)),
                    ping=int(player_data.get('ping', 0)),
                    connected_at=connected_at
                )
                players.append(player)
            
            return players
        except (ValueError, KeyError) as e:
            raise ValidationError(f"Invalid players data: {str(e)}")
    
    def get_player_info(self, player_id: Union[int, str]) -> Optional[DCSPlayer]:
        """Get specific player information"""
        try:
            data = self._make_request('GET', f'/server/players/{player_id}')
            
            if not data:
                return None
            
            # Parse connected time
            connected_str = data.get('connected_at', '')
            if connected_str:
                connected_at = datetime.fromisoformat(connected_str.replace('Z', '+00:00'))
            else:
                connected_at = datetime.now(timezone.utc)
            
            return DCSPlayer(
                name=sanitize_string(data.get('name', ''), max_length=100),
                ucid=sanitize_string(data.get('ucid', ''), max_length=50),
                id=int(data.get('id', 0)),
                side=sanitize_string(data.get('side', ''), max_length=10),
                slot=sanitize_string(data.get('slot', ''), max_length=100),
                unit_type=sanitize_string(data.get('unit_type', ''), max_length=50),
                unit_name=sanitize_string(data.get('unit_name', ''), max_length=100),
                group_id=int(data.get('group_id', 0)),
                ping=int(data.get('ping', 0)),
                connected_at=connected_at
            )
        except (ValueError, KeyError) as e:
            raise ValidationError(f"Invalid player data: {str(e)}")
    
    def get_mission_info(self) -> DCSMission:
        """Get current mission information"""
        try:
            data = self._make_request('GET', '/server/mission')
            
            # Parse timestamps
            start_time_str = data.get('start_time', '')
            if start_time_str:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            else:
                start_time = datetime.now(timezone.utc)
            
            end_time = None
            end_time_str = data.get('end_time', '')
            if end_time_str:
                end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
            
            return DCSMission(
                name=sanitize_string(data.get('name', ''), max_length=200),
                description=sanitize_string(data.get('description', ''), max_length=500),
                theatre=sanitize_string(data.get('theatre', ''), max_length=50),
                start_time=start_time,
                end_time=end_time,
                duration=int(data.get('duration', 0)),
                weather=data.get('weather', {}),
                briefing=sanitize_string(data.get('briefing', ''), max_length=1000)
            )
        except (ValueError, KeyError) as e:
            raise ValidationError(f"Invalid mission data: {str(e)}")
    
    def kick_player(self, player_id: Union[int, str], reason: str = "") -> bool:
        """Kick a player from the server"""
        data = {"reason": sanitize_string(reason, max_length=200)} if reason else {}
        result = self._make_request('POST', f'/server/players/{player_id}/kick', data=data)
        return result.get('success', False)
    
    def ban_player(self, player_id: Union[int, str], reason: str = "", duration: int = 0) -> bool:
        """Ban a player from the server"""
        data = {
            "reason": sanitize_string(reason, max_length=200),
            "duration": duration
        }
        result = self._make_request('POST', f'/server/players/{player_id}/ban', data=data)
        return result.get('success', False)
    
    def unban_player(self, player_id: Union[int, str]) -> bool:
        """Unban a player from the server"""
        result = self._make_request('DELETE', f'/server/players/{player_id}/ban')
        return result.get('success', False)
    
    def send_chat_message(self, message: str, coalition: str = "all") -> bool:
        """Send a chat message to the server"""
        data = {
            "message": sanitize_string(message, max_length=200),
            "coalition": sanitize_string(coalition, max_length=10)
        }
        result = self._make_request('POST', '/server/chat', data=data)
        return result.get('success', False)
    
    def restart_mission(self) -> bool:
        """Restart the current mission"""
        result = self._make_request('POST', '/server/mission/restart')
        return result.get('success', False)
    
    def load_mission(self, mission_name: str) -> bool:
        """Load a specific mission"""
        data = {"mission": sanitize_string(mission_name, max_length=200)}
        result = self._make_request('POST', '/server/mission/load', data=data)
        return result.get('success', False)
    
    def get_available_missions(self) -> List[str]:
        """Get list of available missions"""
        data = self._make_request('GET', '/server/missions')
        missions = data.get('missions', [])
        return [sanitize_string(mission, max_length=200) for mission in missions]
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        return self._make_request('GET', '/server/stats')
    
    def get_player_stats(self, player_id: Union[int, str]) -> Dict[str, Any]:
        """Get player statistics"""
        return self._make_request('GET', f'/server/players/{player_id}/stats')

# Global REST API client instance
dcs_rest_api = None

def initialize_dcs_rest_api():
    """Initialize the DCS REST API client"""
    global dcs_rest_api
    
    if DCS_REST_API_ENABLED and DCS_REST_API_URL:
        try:
            dcs_rest_api = DCSRestAPI()
            logger.info(f"DCS REST API client initialized: {DCS_REST_API_URL}")
        except Exception as e:
            logger.error(f"Failed to initialize DCS REST API client: {e}")
            dcs_rest_api = None
    else:
        logger.info("DCS REST API integration disabled")

def get_dcs_rest_api() -> Optional[DCSRestAPI]:
    """Get the DCS REST API client instance"""
    return dcs_rest_api

def is_dcs_rest_api_enabled() -> bool:
    """Check if DCS REST API integration is enabled"""
    return DCS_REST_API_ENABLED and dcs_rest_api is not None 