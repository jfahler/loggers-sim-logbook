# 🚀 Remote DCSServerBot Setup Guide

## 📋 Network Configuration

**Loggers Backend (This Computer):**
- IP Address: `10.0.0.192`
- Port: `5000`
- URL: `http://10.0.0.192:5000`

**DCSServerBot (Remote DCS Server):**
- Must be able to reach `10.0.0.192:5000`
- Webhook URLs configured to point to Loggers backend

## 🔧 Setup Steps

### Step 1: Configure Loggers Backend

1. **Add environment variables** to your Loggers backend `.env` file:
```env
DCS_BOT_ENABLED=true
DCS_BOT_WEBHOOK_SECRET=loggers_webhook_secret_2024
```

2. **Start your Loggers backend**:
```bash
cd backend
python app.py
```

3. **Verify it's accessible** from the remote server:
```bash
# From the remote DCS server, test connectivity:
curl http://10.0.0.192:5000/health
```

### Step 2: Configure DCSServerBot (Remote Server)

1. **Copy these files** to your remote DCSServerBot `plugins/` directory:
   - `userstats_remote.yaml` → `plugins/userstats.yaml`
   - `missionstats_remote.yaml` → `plugins/missionstats.yaml`

2. **Restart DCSServerBot**:
```bash
cd YourDCSServerBot
./restart.py
```

### Step 3: Test Network Connectivity

From the remote DCS server, test the webhook endpoints:

```bash
# Test USERSTATS endpoint
curl -X POST http://10.0.0.192:5000/dcs/userstats \
  -H "Content-Type: application/json" \
  -H "X-DCS-Signature: loggers_webhook_secret_2024" \
  -d '{"player_name": "TestPilot", "player_ucid": "test", "server_name": "Test", "mission_name": "Test"}'

# Test MISSIONSTATS endpoint
curl -X POST http://10.0.0.192:5000/dcs/missionstats \
  -H "Content-Type: application/json" \
  -H "X-DCS-Signature: loggers_webhook_secret_2024" \
  -d '{"mission_name": "Test", "server_name": "Test", "start_time": "2024-01-01T10:00:00Z"}'
```

## 🔍 Network Troubleshooting

### Check Connectivity
```bash
# From remote server to Loggers backend
ping 10.0.0.192
telnet 10.0.0.192 5000
curl http://10.0.0.192:5000/health
```

### Firewall Configuration
Ensure these ports are open:
- **Loggers Backend**: Port `5000` (TCP)
- **DCSServerBot**: Default ports (usually 50051, 50052)

### Windows Firewall Setup
On the Loggers backend computer (10.0.0.192):

1. **Open Windows Firewall**:
   - Press `Win + R`, type `wf.msc`, press Enter

2. **Create Inbound Rule**:
   - Click "Inbound Rules" → "New Rule"
   - Select "Port" → "TCP" → "Specific local ports: 5000"
   - Select "Allow the connection"
   - Apply to "Domain", "Private", "Public"
   - Name: "Loggers Backend"

3. **Alternative - Command Line**:
```cmd
netsh advfirewall firewall add rule name="Loggers Backend" dir=in action=allow protocol=TCP localport=5000
```

### Common Issues
1. **Firewall blocking**: Configure Windows Firewall to allow port 5000
2. **Router blocking**: Ensure port forwarding if needed
3. **Network isolation**: Check if servers are on same network/subnet
4. **Antivirus blocking**: Add exceptions for Python/Flask

## 📁 File Locations

| File | Source | Remote Destination |
|------|--------|-------------------|
| `userstats_remote.yaml` | `backend/dcs_bot_configs/` | `RemoteDCSServerBot/plugins/userstats.yaml` |
| `missionstats_remote.yaml` | `backend/dcs_bot_configs/` | `RemoteDCSServerBot/plugins/missionstats.yaml` |
| Environment vars | `backend/dcs_bot_configs/loggers_env_remote.txt` | `backend/.env` (local) |

## 🔐 Security Considerations

- **Use HTTPS** in production environments
- **Configure firewall rules** to restrict access to specific IPs
- **Use strong webhook secrets** (change from default)
- **Consider VPN** for secure communication
- **Monitor logs** for unauthorized access attempts

## 🚨 Troubleshooting

### Webhook Not Receiving Data
- ✅ Network connectivity between servers
- ✅ Firewall rules allow traffic
- ✅ Loggers backend accessible from remote server
- ✅ DCSServerBot plugins enabled

### Connection Refused
- ✅ Loggers backend running and listening on 10.0.0.192:5000
- ✅ Firewall allows incoming connections
- ✅ Network routing is correct

### Timeout Errors
- ✅ Network latency between servers
- ✅ Firewall not blocking long-running connections
- ✅ Both services have sufficient resources

### "Connection Refused" Error
1. **Check if Loggers backend is running**:
   ```bash
   # On Loggers backend computer
   netstat -an | findstr :5000
   ```

2. **Check Windows Firewall**:
   ```cmd
   netsh advfirewall firewall show rule name="Loggers Backend"
   ```

3. **Test local access**:
   ```bash
   curl http://localhost:5000/health
   ```

### "No Route to Host" Error
1. **Check network connectivity**:
   ```bash
   ping 10.0.0.192
   tracert 10.0.0.192
   ```

2. **Check router settings**:
   - Ensure both devices are on same network
   - Check for any network isolation features

## 🧪 Testing Commands

### From Remote DCS Server
```bash
# Basic connectivity test
curl http://10.0.0.192:5000/health

# Test USERSTATS webhook
curl -X POST http://10.0.0.192:5000/dcs/userstats \
  -H "Content-Type: application/json" \
  -H "X-DCS-Signature: loggers_webhook_secret_2024" \
  -d '{"player_name": "TestPilot", "player_ucid": "test", "server_name": "Test", "mission_name": "Test"}'

# Test MISSIONSTATS webhook
curl -X POST http://10.0.0.192:5000/dcs/missionstats \
  -H "Content-Type: application/json" \
  -H "X-DCS-Signature: loggers_webhook_secret_2024" \
  -d '{"mission_name": "Test", "server_name": "Test", "start_time": "2024-01-01T10:00:00Z"}'
```

### From Loggers Backend Computer
```bash
# Check if service is running
netstat -an | findstr :5000

# Test local access
curl http://localhost:5000/health

# Check firewall rules
netsh advfirewall firewall show rule name="Loggers Backend"
```

## 📞 Need Help?

1. **Check Loggers backend logs** for error details
2. **Check DCSServerBot logs** for webhook errors
3. **Test network connectivity** between servers
4. **Verify firewall configuration** on both machines
5. **Check Windows Event Viewer** for firewall/network errors

## 🎯 Success Indicators

When everything is working correctly:

1. **Health check returns**:
   ```json
   {
     "status": "healthy",
     "dcs_bot_enabled": true,
     "dcs_bot_webhook_configured": true
   }
   ```

2. **Webhook tests return**:
   ```json
   {
     "success": true,
     "message": "USERSTATS processed successfully"
   }
   ```

3. **DCS missions automatically update** pilot profiles in real-time
4. **Discord notifications** are sent (if configured)
5. **Mission summary files** are generated in `backend/uploads/`

---

**🎉 You're all set!** Once configured, your remote DCS server will automatically send mission data to your Loggers backend, updating pilot profiles in real-time. 