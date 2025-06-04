import os
from datetime import datetime
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook, DiscordEmbed
from dateutil.parser import parse as parse_dt

# Load environment variables from .env
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def format_duration(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours:
        return f"{hours}h {minutes}m"
    elif minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def send_pilot_stats(data: dict) -> dict:
    if not DISCORD_WEBHOOK_URL:
        return {"success": False, "message": "Discord webhook URL not configured"}

    total_kills = data.get("totalAaKills", 0) + data.get("totalAgKills", 0)
    deaths = data.get("totalDeaths", 0)

    if deaths == 0:
        kd_ratio = "∞" if total_kills > 0 else "N/A"
    else:
        kd_ratio = f"{total_kills / deaths:.2f}"

    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)

    embed = DiscordEmbed(
        title="📊 Pilot Statistics",
        color="0099ff",
        timestamp=datetime.utcnow()
    )
    embed.add_embed_field(name="Pilot", value=f"{data['pilotName']} ({data.get('pilotCallsign', 'N/A')})", inline=False)
    embed.add_embed_field(name="Total Flights", value=str(data.get("totalFlights", 0)), inline=True)
    embed.add_embed_field(name="Total Flight Time", value=format_duration(data.get("totalFlightTime", 0)), inline=True)
    embed.add_embed_field(name="Avg Flight Duration", value=format_duration(data.get("averageFlightDuration", 0)), inline=True)
    embed.add_embed_field(name="A-A Kills", value=str(data.get("totalAaKills", 0)), inline=True)
    embed.add_embed_field(name="A-G Kills", value=str(data.get("totalAgKills", 0)), inline=True)
    embed.add_embed_field(name="Total Kills", value=str(total_kills), inline=True)
    embed.add_embed_field(name="Friendly Kills", value=str(data.get("totalFratKills", 0)), inline=True)
    embed.add_embed_field(name="RTBs", value=str(data.get("totalRtbCount", 0)), inline=True)
    embed.add_embed_field(name="Ejections", value=str(data.get("totalEjections", 0)), inline=True)
    embed.add_embed_field(name="Deaths", value=str(deaths), inline=True)
    embed.add_embed_field(name="K/D Ratio", value=kd_ratio, inline=True)
    embed.add_embed_field(name="Favorite Aircraft", value=data.get("favoriteAircraft", "Unknown"), inline=False)
    embed.set_footer(text="DCS Pilot Logbook")

    webhook.add_embed(embed)

    try:
        response = webhook.execute()
        if response.status_code == 200:
            return {"success": True, "message": "Pilot stats sent to Discord"}
        return {"success": False, "message": f"Failed with status {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


def send_flight_summary(data: dict) -> dict:
    if not DISCORD_WEBHOOK_URL:
        return {"success": False, "message": "Discord webhook URL not configured"}

    # Handle timestamp parsing
    timestamp_value = data.get("startTime")
    if isinstance(timestamp_value, str):
        try:
            timestamp_value = parse_dt(timestamp_value)
        except Exception:
            timestamp_value = datetime.utcnow()
    elif not isinstance(timestamp_value, datetime):
        timestamp_value = datetime.utcnow()

    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)

    embed = DiscordEmbed(
        title="🛩️ Flight Summary",
        color="00ff00",
        timestamp=timestamp_value
    )
    embed.add_embed_field(name="Pilot", value=f"{data['pilotName']} ({data.get('pilotCallsign', 'N/A')})", inline=True)
    embed.add_embed_field(name="Aircraft", value=data.get("aircraftType", "Unknown"), inline=True)
    embed.add_embed_field(name="Mission", value=data.get("missionName", "Unknown"), inline=True)
    embed.add_embed_field(name="Duration", value=format_duration(data.get("durationSeconds", 0)), inline=True)
    embed.add_embed_field(name="A-A Kills", value=str(data.get("aaKills", 0)), inline=True)
    embed.add_embed_field(name="A-G Kills", value=str(data.get("agKills", 0)), inline=True)
    embed.add_embed_field(name="Friendly Kills", value=str(data.get("fratKills", 0)), inline=True)
    embed.add_embed_field(name="RTBs", value=str(data.get("rtbCount", 0)), inline=True)
    embed.add_embed_field(name="Ejections", value=str(data.get("ejections", 0)), inline=True)
    embed.add_embed_field(name="Deaths", value=str(data.get("deaths", 0)), inline=True)
    embed.set_footer(text="DCS Pilot Logbook")

    webhook.add_embed(embed)

    try:
        response = webhook.execute()
        if response.status_code == 200:
            return {"success": True, "message": "Flight summary sent to Discord"}
        return {"success": False, "message": f"Failed with status {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
