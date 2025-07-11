"""
DCS Server Bot Integration Module

This module provides integration with DCSServerBot's USERSTATS and MISSIONSTATS plugins.
It handles webhook endpoints that receive real-time data from DCS missions.

Based on DCSServerBot documentation:
- USERSTATS: https://github.com/Special-K-s-Flightsim-Bots/DCSServerBot/blob/master/plugins/userstats/README.md
- MISSIONSTATS: https://github.com/Special-K-s-Flightsim-Bots/DCSServerBot/blob/master/plugins/missionstats/README.md
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from validation import sanitize_string, ValidationError
from error_handling import APIError, ErrorCodes, log_operation_start, log_operation_success, log_operation_failure
from webhook_helpers import send_pilot_stats, send_flight_summary

logger = logging.getLogger(__name__)

# Configuration
DCS_BOT_WEBHOOK_SECRET = os.getenv("DCS_BOT_WEBHOOK_SECRET", "")
DCS_BOT_ENABLED = os.getenv("DCS_BOT_ENABLED", "false").lower() == "true"

@dataclass
class DCSUserStats:
    """Data structure for USERSTATS webhook data"""
    player_name: str
    player_ucid: str
    player_id: int
    server_name: str
    mission_name: str
    mission_id: str
    flight_time: int  # in seconds
    kills: Dict[str, int]  # aircraft_type -> count
    deaths: int
    ejections: int
    crashes: int
    aircraft_type: str
    side: str  # "red" or "blue"
    timestamp: datetime

@dataclass
class DCSMissionStats:
    """Data structure for MISSIONSTATS webhook data"""
    mission_name: str
    mission_id: str
    server_name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: int  # in seconds
    players: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    timestamp: datetime

def validate_dcs_bot_webhook(data: Dict[str, Any], webhook_type: str) -> bool:
    """Validate DCS Server Bot webhook data"""
    if not data:
        return False, "No data provided"
    
    if webhook_type == "userstats":
        required_fields = ["player_name", "player_ucid", "server_name", "mission_name"]
    elif webhook_type == "missionstats":
        required_fields = ["mission_name", "server_name", "start_time"]
    else:
        return False, f"Invalid webhook type: {webhook_type}"
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    return True, ""

def parse_userstats_data(data: Dict[str, Any]) -> DCSUserStats:
    """Parse and validate USERSTATS webhook data"""
    try:
        # Parse timestamp
        timestamp_str = data.get("timestamp", "")
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            timestamp = datetime.now(timezone.utc)
        
        # Parse kills dictionary
        kills = data.get("kills", {})
        if isinstance(kills, str):
            try:
                kills = json.loads(kills)
            except json.JSONDecodeError:
                kills = {}
        
        return DCSUserStats(
            player_name=sanitize_string(data["player_name"], max_length=100),
            player_ucid=sanitize_string(data["player_ucid"], max_length=50),
            player_id=int(data.get("player_id", 0)),
            server_name=sanitize_string(data["server_name"], max_length=100),
            mission_name=sanitize_string(data["mission_name"], max_length=200),
            mission_id=sanitize_string(data.get("mission_id", ""), max_length=50),
            flight_time=int(data.get("flight_time", 0)),
            kills=kills,
            deaths=int(data.get("deaths", 0)),
            ejections=int(data.get("ejections", 0)),
            crashes=int(data.get("crashes", 0)),
            aircraft_type=sanitize_string(data.get("aircraft_type", "Unknown"), max_length=50),
            side=sanitize_string(data.get("side", "unknown"), max_length=10),
            timestamp=timestamp
        )
    except (ValueError, KeyError) as e:
        raise ValidationError(f"Invalid USERSTATS data: {str(e)}")

def parse_missionstats_data(data: Dict[str, Any]) -> DCSMissionStats:
    """Parse and validate MISSIONSTATS webhook data"""
    try:
        # Parse timestamps
        start_time_str = data.get("start_time", "")
        if start_time_str:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        else:
            start_time = datetime.now(timezone.utc)
        
        end_time = None
        end_time_str = data.get("end_time", "")
        if end_time_str:
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        
        # Parse players list
        players = data.get("players", [])
        if isinstance(players, str):
            try:
                players = json.loads(players)
            except json.JSONDecodeError:
                players = []
        
        # Parse statistics
        statistics = data.get("statistics", {})
        if isinstance(statistics, str):
            try:
                statistics = json.loads(statistics)
            except json.JSONDecodeError:
                statistics = {}
        
        return DCSMissionStats(
            mission_name=sanitize_string(data["mission_name"], max_length=200),
            mission_id=sanitize_string(data.get("mission_id", ""), max_length=50),
            server_name=sanitize_string(data["server_name"], max_length=100),
            start_time=start_time,
            end_time=end_time,
            duration=int(data.get("duration", 0)),
            players=players,
            statistics=statistics,
            timestamp=datetime.now(timezone.utc)
        )
    except (ValueError, KeyError) as e:
        raise ValidationError(f"Invalid MISSIONSTATS data: {str(e)}")

def process_userstats_webhook(userstats: DCSUserStats) -> Dict[str, Any]:
    """Process USERSTATS data and update pilot profiles"""
    operation = "dcs_userstats_processing"
    
    try:
        log_operation_start(operation, {
            "player_name": userstats.player_name,
            "mission_name": userstats.mission_name,
            "server_name": userstats.server_name
        })
        
        # Calculate total kills
        total_kills = sum(userstats.kills.values())
        
        # Prepare pilot data for profile update
        pilot_data = {
            "pilot_name": userstats.player_name,
            "callsign": userstats.player_ucid,
            "mission": {
                "name": userstats.mission_name,
                "server": userstats.server_name,
                "aircraft": userstats.aircraft_type,
                "side": userstats.side,
                "flight_time": userstats.flight_time,
                "aa_kills": userstats.kills.get("air", 0),
                "ag_kills": userstats.kills.get("ground", 0),
                "frat_kills": userstats.kills.get("friendly", 0),
                "deaths": userstats.deaths,
                "ejections": userstats.ejections,
                "crashes": userstats.crashes,
                "rtb": 1 if userstats.deaths == 0 and userstats.ejections == 0 else 0,
                "date": userstats.timestamp.isoformat()
            }
        }
        
        # Import here to avoid circular imports
        from update_profiles import update_profiles_from_data
        from generate_index import generate_index
        
        # Update pilot profile
        update_profiles_from_data({userstats.player_name: pilot_data})
        generate_index()
        
        # Send Discord notification if configured
        if os.getenv("DISCORD_WEBHOOK_URL"):
            discord_data = {
                "pilotName": userstats.player_name,
                "pilotCallsign": userstats.player_ucid,
                "aircraftType": userstats.aircraft_type,
                "missionName": userstats.mission_name,
                "startTime": userstats.timestamp.isoformat(),
                "durationSeconds": userstats.flight_time,
                "aaKills": userstats.kills.get("air", 0),
                "agKills": userstats.kills.get("ground", 0),
                "fratKills": userstats.kills.get("friendly", 0),
                "rtbCount": 1 if userstats.deaths == 0 and userstats.ejections == 0 else 0,
                "ejections": userstats.ejections,
                "deaths": userstats.deaths
            }
            send_flight_summary(discord_data)
        
        log_operation_success(operation, {
            "player_name": userstats.player_name,
            "total_kills": total_kills,
            "flight_time": userstats.flight_time
        })
        
        return {
            "success": True,
            "message": f"Processed stats for {userstats.player_name}",
            "player_name": userstats.player_name,
            "total_kills": total_kills,
            "flight_time": userstats.flight_time
        }
        
    except Exception as e:
        log_operation_failure(operation, e, {
            "player_name": userstats.player_name,
            "mission_name": userstats.mission_name
        })
        raise APIError(
            error_code=ErrorCodes.DATA_PROCESSING_FAILED,
            message=f"Failed to process USERSTATS: {str(e)}",
            status_code=500
        )

def process_missionstats_webhook(missionstats: DCSMissionStats) -> Dict[str, Any]:
    """Process MISSIONSTATS data and generate mission summary"""
    operation = "dcs_missionstats_processing"
    
    try:
        log_operation_start(operation, {
            "mission_name": missionstats.mission_name,
            "server_name": missionstats.server_name,
            "players_count": len(missionstats.players)
        })
        
        # Process each player's stats
        processed_players = []
        for player in missionstats.players:
            if isinstance(player, dict) and "name" in player:
                player_name = sanitize_string(player["name"], max_length=100)
                player_stats = {
                    "name": player_name,
                    "ucid": sanitize_string(player.get("ucid", ""), max_length=50),
                    "flight_time": int(player.get("flight_time", 0)),
                    "kills": player.get("kills", {}),
                    "deaths": int(player.get("deaths", 0)),
                    "ejections": int(player.get("ejections", 0)),
                    "aircraft": sanitize_string(player.get("aircraft", "Unknown"), max_length=50)
                }
                processed_players.append(player_stats)
        
        # Generate mission summary
        mission_summary = {
            "mission_name": missionstats.mission_name,
            "server_name": missionstats.server_name,
            "start_time": missionstats.start_time.isoformat(),
            "end_time": missionstats.end_time.isoformat() if missionstats.end_time else None,
            "duration": missionstats.duration,
            "players_count": len(processed_players),
            "players": processed_players,
            "statistics": missionstats.statistics
        }
        
        # Save mission summary to file
        mission_file = f"mission_{missionstats.mission_id}_{int(missionstats.timestamp.timestamp())}.json"
        mission_path = os.path.join("uploads", mission_file)
        
        os.makedirs("uploads", exist_ok=True)
        with open(mission_path, 'w') as f:
            json.dump(mission_summary, f, indent=2, default=str)
        
        log_operation_success(operation, {
            "mission_name": missionstats.mission_name,
            "players_count": len(processed_players),
            "duration": missionstats.duration
        })
        
        return {
            "success": True,
            "message": f"Processed mission stats for {missionstats.mission_name}",
            "mission_name": missionstats.mission_name,
            "players_count": len(processed_players),
            "duration": missionstats.duration,
            "mission_file": mission_file
        }
        
    except Exception as e:
        log_operation_failure(operation, e, {
            "mission_name": missionstats.mission_name,
            "server_name": missionstats.server_name
        })
        raise APIError(
            error_code=ErrorCodes.DATA_PROCESSING_FAILED,
            message=f"Failed to process MISSIONSTATS: {str(e)}",
            status_code=500
        )

def verify_webhook_signature(request_data: str, signature: str) -> bool:
    """Verify webhook signature if configured"""
    if not DCS_BOT_WEBHOOK_SECRET:
        # If no secret configured, accept all requests
        return True
    
    # Simple signature verification (can be enhanced with HMAC)
    expected_signature = f"sha256={DCS_BOT_WEBHOOK_SECRET}"
    return signature == expected_signature 