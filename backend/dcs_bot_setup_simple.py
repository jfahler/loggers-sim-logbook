#!/usr/bin/env python3
"""
DCSServerBot Configuration Helper (Simple Version)

This script helps you configure DCSServerBot to work with the Loggers integration.
It generates the necessary configuration files and provides setup instructions.
"""

import os
import json

def generate_userstats_yaml(webhook_url: str, webhook_secret: str) -> str:
    """Generate USERSTATS plugin YAML configuration"""
    return f"""userstats:
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
"""

def generate_missionstats_yaml(webhook_url: str, webhook_secret: str) -> str:
    """Generate MISSIONSTATS plugin YAML configuration"""
    missionstats_url = webhook_url.replace('/dcs/userstats', '/dcs/missionstats')
    return f"""missionstats:
  enabled: true
  webhook_url: "{missionstats_url}"
  webhook_secret: "{webhook_secret}"
  send_on_mission_end: true
  include_player_stats: true
  include_mission_summary: true
  include_aircraft_usage: true
  include_kill_statistics: true
"""

def save_file(content: str, filename: str, output_dir: str = "dcs_bot_configs"):
    """Save content to file"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    return filepath

def generate_setup_instructions(webhook_url: str, webhook_secret: str) -> str:
    """Generate setup instructions"""
    return f"""# DCSServerBot Setup Instructions for Loggers Integration

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

2. Edit or create `userstats.yaml` with the following content:
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

## Step 4: Configure Loggers Backend

Add these lines to your Loggers backend `.env` file:
```env
DCS_BOT_ENABLED=true
DCS_BOT_WEBHOOK_SECRET={webhook_secret}
```

## Step 5: Restart Services

1. Restart DCSServerBot:
   ```bash
   ./restart.py
   ```

2. Restart your Loggers backend:
   ```bash
   # Stop the current backend process
   # Then start it again
   python app.py
   ```

## Step 6: Test the Integration

1. Start a DCS mission
2. Have players join and complete the mission
3. Check your Loggers backend logs for incoming webhook data
4. Verify pilot profiles are updated in the web interface

## Step 7: Verify Configuration

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

## DCSServerBot Directory Structure

Your DCSServerBot installation should look something like this:
```
DCSServerBot/
├── plugins/
│   ├── userstats.yaml      # Copy the generated file here
│   ├── missionstats.yaml   # Copy the generated file here
│   └── ...
├── update.py
├── restart.py
├── status.py
└── ...
```

## Finding Your DCSServerBot Installation

If you're not sure where DCSServerBot is installed:
1. Look for a directory named "DCSServerBot" or similar
2. Check common locations:
   - C:\\DCSServerBot\\
   - C:\\Users\\YourUsername\\DCSServerBot\\
   - C:\\Program Files\\DCSServerBot\\
3. Look for files like `update.py`, `restart.py`, or `status.py`
"""

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
    
    print(f"Default webhook URL: {default_url}")
    print(f"Default webhook secret: {default_secret}")
    print("\nPress Enter to use defaults, or enter custom values:")
    
    webhook_url = input(f"Enter webhook URL for USERSTATS: ").strip()
    if not webhook_url:
        webhook_url = default_url
    
    webhook_secret = input(f"Enter webhook secret: ").strip()
    if not webhook_secret:
        webhook_secret = default_secret
    
    print(f"\n✅ Using configuration:")
    print(f"   Webhook URL: {webhook_url}")
    print(f"   Webhook Secret: {webhook_secret}")
    
    # Generate configurations
    print("\n🔧 Generating configuration files...")
    
    userstats_yaml = generate_userstats_yaml(webhook_url, webhook_secret)
    missionstats_yaml = generate_missionstats_yaml(webhook_url, webhook_secret)
    
    # Save configurations
    userstats_file = save_file(userstats_yaml, "userstats.yaml")
    missionstats_file = save_file(missionstats_yaml, "missionstats.yaml")
    
    print(f"✅ USERSTATS config saved to: {userstats_file}")
    print(f"✅ MISSIONSTATS config saved to: {missionstats_file}")
    
    # Generate instructions
    instructions = generate_setup_instructions(webhook_url, webhook_secret)
    instructions_file = save_file(instructions, "SETUP_INSTRUCTIONS.md")
    
    print(f"✅ Setup instructions saved to: {instructions_file}")
    
    # Generate .env snippet
    env_snippet = f"""# Add these to your Loggers backend .env file:
DCS_BOT_ENABLED=true
DCS_BOT_WEBHOOK_SECRET={webhook_secret}
"""
    
    env_file = save_file(env_snippet, "loggers_env_snippet.txt")
    print(f"✅ Environment variables saved to: {env_file}")
    
    # Show the generated files
    print("\n📄 Generated Files:")
    print("-" * 30)
    print(f"1. {userstats_file}")
    print(f"2. {missionstats_file}")
    print(f"3. {instructions_file}")
    print(f"4. {env_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 Configuration Complete!")
    print("\n📋 Next Steps:")
    print("1. Find your DCSServerBot installation directory")
    print("2. Copy userstats.yaml and missionstats.yaml to the plugins/ directory")
    print("3. Add the environment variables to your Loggers backend .env file")
    print("4. Restart DCSServerBot: ./restart.py")
    print("5. Restart your Loggers backend")
    print("6. Test the integration with a DCS mission")
    print("\n📖 See SETUP_INSTRUCTIONS.md for detailed instructions")
    print("🔧 See loggers_env_snippet.txt for environment variables")
    
    # Show the YAML content
    print("\n📋 USERSTATS Configuration (userstats.yaml):")
    print("-" * 40)
    print(userstats_yaml)
    
    print("\n📋 MISSIONSTATS Configuration (missionstats.yaml):")
    print("-" * 40)
    print(missionstats_yaml)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Please check your configuration and try again") 