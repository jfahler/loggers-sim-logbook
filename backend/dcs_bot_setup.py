#!/usr/bin/env python3
"""
DCSServerBot Configuration Helper

This script helps you configure DCSServerBot to work with the Loggers integration.
It generates the necessary configuration files and provides setup instructions.
"""

import os
import json
import yaml
from pathlib import Path

def generate_userstats_config(webhook_url: str, webhook_secret: str) -> dict:
    """Generate USERSTATS plugin configuration"""
    return {
        "userstats": {
            "enabled": True,
            "webhook_url": webhook_url,
            "webhook_secret": webhook_secret,
            "send_on_mission_end": True,
            "send_on_player_leave": True,
            "include_flight_time": True,
            "include_kills": True,
            "include_deaths": True,
            "include_ejections": True,
            "include_crashes": True,
            "include_aircraft": True,
            "include_side": True
        }
    }

def generate_missionstats_config(webhook_url: str, webhook_secret: str) -> dict:
    """Generate MISSIONSTATS plugin configuration"""
    return {
        "missionstats": {
            "enabled": True,
            "webhook_url": webhook_url,
            "webhook_secret": webhook_secret,
            "send_on_mission_end": True,
            "include_player_stats": True,
            "include_mission_summary": True,
            "include_aircraft_usage": True,
            "include_kill_statistics": True
        }
    }

def save_yaml_config(config: dict, filename: str, output_dir: str = "dcs_bot_configs"):
    """Save configuration to YAML file"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    return filepath

def generate_setup_instructions(webhook_url: str, webhook_secret: str):
    """Generate setup instructions"""
    instructions = f"""
# DCSServerBot Setup Instructions for Loggers Integration

## Prerequisites
- DCSServerBot installed and running
- Loggers backend running on {webhook_url.replace('/dcs/userstats', '')}

## Step 1: Install Required Plugins

In your DCSServerBot directory, run:
```bash
./update.py -y
```

This will install/update the USERSTATS and MISSIONSTATS plugins.

## Step 2: Configure USERSTATS Plugin

1. Navigate to your DCSServerBot plugins directory:
   ```bash
   cd plugins
   ```

2. Edit or create `userstats.yaml`:
   ```yaml
   userstats:
     enabled: true
     webhook_url: "{webhook_url}"
     webhook_secret: "{webhook_secret}"
     send_on_mission_end: true
     send_on_player_leave: true
     include_flight_time: true
     include_kills: true
     include_deaths: true
     include_ejections: true
     include_crashes: true
     include_aircraft: true
     include_side: true
   ```

## Step 3: Configure MISSIONSTATS Plugin

1. In the same plugins directory, edit or create `missionstats.yaml`:
   ```yaml
   missionstats:
     enabled: true
     webhook_url: "{webhook_url.replace('/dcs/userstats', '/dcs/missionstats')}"
     webhook_secret: "{webhook_secret}"
     send_on_mission_end: true
     include_player_stats: true
     include_mission_summary: true
     include_aircraft_usage: true
     include_kill_statistics: true
   ```

## Step 4: Restart DCSServerBot

After making configuration changes:
```bash
./restart.py
```

## Step 5: Test the Integration

1. Start a DCS mission
2. Have players join and complete the mission
3. Check your Loggers backend logs for incoming webhook data
4. Verify pilot profiles are updated in the web interface

## Step 6: Verify Configuration

You can test the webhook endpoints manually:

```bash
# Test USERSTATS endpoint
curl -X POST {webhook_url} \\
  -H "Content-Type: application/json" \\
  -H "X-DCS-Signature: {webhook_secret}" \\
  -d '{{"player_name": "TestPilot", "player_ucid": "test", "server_name": "Test", "mission_name": "Test"}}'

# Test MISSIONSTATS endpoint
curl -X POST {webhook_url.replace('/dcs/userstats', '/dcs/missionstats')} \\
  -H "Content-Type: application/json" \\
  -H "X-DCS-Signature: {webhook_secret}" \\
  -d '{{"mission_name": "Test", "server_name": "Test", "start_time": "2024-01-01T10:00:00Z"}}'
```

## Troubleshooting

### Webhook Not Receiving Data
- Check if DCSServerBot is running: `./status.py`
- Verify webhook URLs are accessible from DCSServerBot
- Check DCSServerBot logs for errors
- Ensure plugins are enabled in configuration

### Signature Verification Failed
- Verify webhook_secret matches in both DCSServerBot and Loggers config
- Check that X-DCS-Signature header is being sent
- Ensure no extra spaces or characters in the secret

### Data Not Processing
- Check Loggers backend logs for validation errors
- Verify required fields are present in webhook data
- Ensure Loggers backend is running and accessible

## Configuration Files Generated

The following configuration files have been generated in the 'dcs_bot_configs' directory:
- userstats.yaml
- missionstats.yaml

Copy these files to your DCSServerBot plugins directory and restart the bot.

## Security Notes

- Keep your webhook_secret secure and don't share it
- Use HTTPS in production environments
- Consider firewall rules to restrict webhook access
- Regularly update DCSServerBot and its plugins
"""
    
    return instructions

def main():
    """Main setup function"""
    print("🚀 DCSServerBot Configuration Helper for Loggers Integration")
    print("=" * 60)
    
    # Get configuration from user
    print("\n📝 Configuration Setup")
    print("-" * 30)
    
    # Default values
    default_url = "http://localhost:5000/dcs/userstats"
    default_secret = "loggers_webhook_secret_2024"
    
    webhook_url = input(f"Enter webhook URL for USERSTATS (default: {default_url}): ").strip()
    if not webhook_url:
        webhook_url = default_url
    
    webhook_secret = input(f"Enter webhook secret (default: {default_secret}): ").strip()
    if not webhook_secret:
        webhook_secret = default_secret
    
    print(f"\n✅ Using configuration:")
    print(f"   Webhook URL: {webhook_url}")
    print(f"   Webhook Secret: {webhook_secret}")
    
    # Generate configurations
    print("\n🔧 Generating configuration files...")
    
    userstats_config = generate_userstats_config(webhook_url, webhook_secret)
    missionstats_config = generate_missionstats_config(webhook_url, webhook_secret)
    
    # Save configurations
    userstats_file = save_yaml_config(userstats_config, "userstats.yaml")
    missionstats_file = save_yaml_config(missionstats_config, "missionstats.yaml")
    
    print(f"✅ USERSTATS config saved to: {userstats_file}")
    print(f"✅ MISSIONSTATS config saved to: {missionstats_file}")
    
    # Generate instructions
    instructions = generate_setup_instructions(webhook_url, webhook_secret)
    instructions_file = "dcs_bot_configs/SETUP_INSTRUCTIONS.md"
    
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"✅ Setup instructions saved to: {instructions_file}")
    
    # Generate .env snippet
    env_snippet = f"""
# Add these to your Loggers backend .env file:
DCS_BOT_ENABLED=true
DCS_BOT_WEBHOOK_SECRET={webhook_secret}
"""
    
    env_file = "dcs_bot_configs/loggers_env_snippet.txt"
    with open(env_file, 'w') as f:
        f.write(env_snippet)
    
    print(f"✅ Environment variables saved to: {env_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 Configuration Complete!")
    print("\n📋 Next Steps:")
    print("1. Copy the generated YAML files to your DCSServerBot plugins directory")
    print("2. Add the environment variables to your Loggers backend .env file")
    print("3. Restart DCSServerBot")
    print("4. Restart your Loggers backend")
    print("5. Test the integration with a DCS mission")
    print("\n📖 See SETUP_INSTRUCTIONS.md for detailed instructions")
    print("🔧 See loggers_env_snippet.txt for environment variables")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Please check your configuration and try again") 