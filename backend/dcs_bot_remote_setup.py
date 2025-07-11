#!/usr/bin/env python3
"""
DCSServerBot Remote Configuration Helper

This script helps configure DCSServerBot when it's running on a remote server
separate from the Loggers backend.
"""

import os
import socket

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "192.168.1.100"  # Fallback

def generate_remote_config():
    """Generate configuration for remote DCSServerBot setup"""
    print("🚀 DCSServerBot Remote Configuration Helper")
    print("=" * 50)
    print("\nThis setup is for when DCSServerBot runs on a remote DCS server.")
    print("\n📋 Information needed:")
    print("1. Your Loggers backend IP address (where this script is running)")
    print("2. Your Loggers backend port (default: 5000)")
    print("3. Your webhook secret (for security)")
    
    # Get local IP
    local_ip = get_local_ip()
    print(f"\n🔍 Detected local IP: {local_ip}")
    
    # Get configuration from user
    print("\n📝 Configuration Setup")
    print("-" * 30)
    
    loggers_ip = input(f"Enter Loggers backend IP address (default: {local_ip}): ").strip()
    if not loggers_ip:
        loggers_ip = local_ip
    
    loggers_port = input("Enter Loggers backend port (default: 5000): ").strip()
    if not loggers_port:
        loggers_port = "5000"
    
    webhook_secret = input("Enter webhook secret (default: loggers_webhook_secret_2024): ").strip()
    if not webhook_secret:
        webhook_secret = "loggers_webhook_secret_2024"
    
    # Generate webhook URLs
    userstats_url = f"http://{loggers_ip}:{loggers_port}/dcs/userstats"
    missionstats_url = f"http://{loggers_ip}:{loggers_port}/dcs/missionstats"
    
    print(f"\n✅ Configuration:")
    print(f"   Loggers Backend: http://{loggers_ip}:{loggers_port}")
    print(f"   USERSTATS Webhook: {userstats_url}")
    print(f"   MISSIONSTATS Webhook: {missionstats_url}")
    print(f"   Webhook Secret: {webhook_secret}")
    
    # Generate configuration files
    print("\n🔧 Generating configuration files...")
    
    # USERSTATS config
    userstats_yaml = f"""userstats:
  enabled: true
  webhook_url: "{userstats_url}"
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
    
    # MISSIONSTATS config
    missionstats_yaml = f"""missionstats:
  enabled: true
  webhook_url: "{missionstats_url}"
  webhook_secret: "{webhook_secret}"
  send_on_mission_end: true
  include_player_stats: true
  include_mission_summary: true
  include_aircraft_usage: true
  include_kill_statistics: true
"""
    
    # Save files
    os.makedirs("dcs_bot_configs", exist_ok=True)
    
    with open("dcs_bot_configs/userstats_remote.yaml", "w") as f:
        f.write(userstats_yaml)
    
    with open("dcs_bot_configs/missionstats_remote.yaml", "w") as f:
        f.write(missionstats_yaml)
    
    # Environment variables
    env_snippet = f"""# Add these to your Loggers backend .env file:
DCS_BOT_ENABLED=true
DCS_BOT_WEBHOOK_SECRET={webhook_secret}
"""
    
    with open("dcs_bot_configs/loggers_env_remote.txt", "w") as f:
        f.write(env_snippet)
    
    # Generate setup instructions
    setup_instructions = f"""# 🚀 Remote DCSServerBot Setup Guide

## 📋 Network Configuration

**Loggers Backend (This Computer):**
- IP Address: {loggers_ip}
- Port: {loggers_port}
- URL: http://{loggers_ip}:{loggers_port}

**DCSServerBot (Remote DCS Server):**
- Must be able to reach {loggers_ip}:{loggers_port}
- Webhook URLs configured to point to Loggers backend

## 🔧 Setup Steps

### Step 1: Configure Loggers Backend

1. Add these lines to your Loggers backend `.env` file:
```env
DCS_BOT_ENABLED=true
DCS_BOT_WEBHOOK_SECRET={webhook_secret}
```

2. Start your Loggers backend:
```bash
cd backend
python app.py
```

3. Verify it's accessible from the remote server:
```bash
# From the remote DCS server, test connectivity:
curl http://{loggers_ip}:{loggers_port}/health
```

### Step 2: Configure DCSServerBot (Remote Server)

1. Copy these files to your remote DCSServerBot `plugins/` directory:
   - `userstats_remote.yaml` → `plugins/userstats.yaml`
   - `missionstats_remote.yaml` → `plugins/missionstats.yaml`

2. Restart DCSServerBot:
```bash
cd YourDCSServerBot
./restart.py
```

### Step 3: Test Network Connectivity

From the remote DCS server, test the webhook endpoints:

```bash
# Test USERSTATS endpoint
curl -X POST {userstats_url} \\
  -H "Content-Type: application/json" \\
  -H "X-DCS-Signature: {webhook_secret}" \\
  -d '{{"player_name": "TestPilot", "player_ucid": "test", "server_name": "Test", "mission_name": "Test"}}'

# Test MISSIONSTATS endpoint
curl -X POST {missionstats_url} \\
  -H "Content-Type: application/json" \\
  -H "X-DCS-Signature: {webhook_secret}" \\
  -d '{{"mission_name": "Test", "server_name": "Test", "start_time": "2024-01-01T10:00:00Z"}}'
```

## 🔍 Network Troubleshooting

### Check Connectivity
```bash
# From remote server to Loggers backend
ping {loggers_ip}
telnet {loggers_ip} {loggers_port}
curl http://{loggers_ip}:{loggers_port}/health
```

### Firewall Configuration
Ensure these ports are open:
- **Loggers Backend**: Port {loggers_port} (TCP)
- **DCSServerBot**: Default ports (usually 50051, 50052)

### Common Issues
1. **Firewall blocking**: Configure Windows Firewall to allow port {loggers_port}
2. **Router blocking**: Ensure port forwarding if needed
3. **Network isolation**: Check if servers are on same network/subnet

## 📁 File Locations

| File | Source | Remote Destination |
|------|--------|-------------------|
| `userstats_remote.yaml` | `backend/dcs_bot_configs/` | `RemoteDCSServerBot/plugins/userstats.yaml` |
| `missionstats_remote.yaml` | `backend/dcs_bot_configs/` | `RemoteDCSServerBot/plugins/missionstats.yaml` |
| Environment vars | `backend/dcs_bot_configs/loggers_env_remote.txt` | `backend/.env` (local) |

## 🔐 Security Considerations

- Use HTTPS in production environments
- Configure firewall rules to restrict access
- Use strong webhook secrets
- Consider VPN for secure communication

## 🚨 Troubleshooting

### Webhook Not Receiving Data
- ✅ Network connectivity between servers
- ✅ Firewall rules allow traffic
- ✅ Loggers backend accessible from remote server
- ✅ DCSServerBot plugins enabled

### Connection Refused
- ✅ Loggers backend running and listening on {loggers_ip}:{loggers_port}
- ✅ Firewall allows incoming connections
- ✅ Network routing is correct

### Timeout Errors
- ✅ Network latency between servers
- ✅ Firewall not blocking long-running connections
- ✅ Both services have sufficient resources
"""
    
    with open("dcs_bot_configs/REMOTE_SETUP_GUIDE.md", "w") as f:
        f.write(setup_instructions)
    
    print(f"\n✅ Configuration files generated:")
    print(f"   - dcs_bot_configs/userstats_remote.yaml")
    print(f"   - dcs_bot_configs/missionstats_remote.yaml")
    print(f"   - dcs_bot_configs/loggers_env_remote.txt")
    print(f"   - dcs_bot_configs/REMOTE_SETUP_GUIDE.md")
    
    print(f"\n📋 Next Steps:")
    print(f"1. Copy the remote YAML files to your DCSServerBot plugins directory")
    print(f"2. Add environment variables to your Loggers backend .env file")
    print(f"3. Ensure network connectivity between servers")
    print(f"4. Test the webhook endpoints from the remote server")
    print(f"5. Restart both services")
    
    print(f"\n🔍 Network Test:")
    print(f"From your remote DCS server, test:")
    print(f"   curl http://{loggers_ip}:{loggers_port}/health")
    
    return {
        "loggers_ip": loggers_ip,
        "loggers_port": loggers_port,
        "webhook_secret": webhook_secret,
        "userstats_url": userstats_url,
        "missionstats_url": missionstats_url
    }

if __name__ == "__main__":
    try:
        generate_remote_config()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Please check your configuration and try again") 