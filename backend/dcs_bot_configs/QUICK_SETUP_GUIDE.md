# 🚀 Quick Setup Guide: DCSServerBot + Loggers Integration

## 📋 What You Need

1. **DCSServerBot** - Your existing installation
2. **Loggers Backend** - Running on `http://localhost:5000`
3. **Generated Config Files** - Already created in this directory

## 🔧 Step-by-Step Setup

### Step 1: Find Your DCSServerBot Installation

Look for a directory containing files like:
- `update.py`
- `restart.py` 
- `status.py`
- `plugins/` folder

Common locations:
- `C:\DCSServerBot\`
- `C:\Users\YourUsername\DCSServerBot\`
- `C:\Program Files\DCSServerBot\`

### Step 2: Install/Update Required Plugins

In your DCSServerBot directory, run:
```bash
./update.py -y
```

This installs the USERSTATS and MISSIONSTATS plugins.

### Step 3: Copy Configuration Files

Copy these files to your DCSServerBot `plugins/` directory:

**From:** `backend/dcs_bot_configs/userstats.yaml`
**To:** `YourDCSServerBot/plugins/userstats.yaml`

**From:** `backend/dcs_bot_configs/missionstats.yaml`  
**To:** `YourDCSServerBot/plugins/missionstats.yaml`

### Step 4: Configure Loggers Backend

Add these lines to your Loggers backend `.env` file:
```env
DCS_BOT_ENABLED=true
DCS_BOT_WEBHOOK_SECRET=loggers_webhook_secret_2024
```

### Step 5: Restart Services

1. **Restart DCSServerBot:**
   ```bash
   cd YourDCSServerBot
   ./restart.py
   ```

2. **Restart Loggers Backend:**
   ```bash
   cd backend
   python app.py
   ```

### Step 6: Test the Integration

1. Start a DCS mission
2. Have players join and complete the mission
3. Check Loggers backend logs for webhook data
4. Verify pilot profiles update in the web interface

## 🧪 Manual Testing

Test the webhook endpoints manually:

```bash
# Test USERSTATS endpoint
curl -X POST http://localhost:5000/dcs/userstats \
  -H "Content-Type: application/json" \
  -H "X-DCS-Signature: loggers_webhook_secret_2024" \
  -d '{"player_name": "TestPilot", "player_ucid": "test", "server_name": "Test", "mission_name": "Test"}'

# Test MISSIONSTATS endpoint  
curl -X POST http://localhost:5000/dcs/missionstats \
  -H "Content-Type: application/json" \
  -H "X-DCS-Signature: loggers_webhook_secret_2024" \
  -d '{"mission_name": "Test", "server_name": "Test", "start_time": "2024-01-01T10:00:00Z"}'
```

## 🔍 Verification

### Check DCSServerBot Status
```bash
cd YourDCSServerBot
./status.py
```

### Check Loggers Backend Health
```bash
curl http://localhost:5000/health
```

Should show:
```json
{
  "status": "healthy",
  "dcs_bot_enabled": true,
  "dcs_bot_webhook_configured": true
}
```

## 🚨 Troubleshooting

### Webhook Not Receiving Data
- ✅ DCSServerBot running? `./status.py`
- ✅ Plugins enabled? Check `plugins/userstats.yaml` and `plugins/missionstats.yaml`
- ✅ URLs accessible? Test with curl commands above
- ✅ Loggers backend running? Check `http://localhost:5000/health`

### Signature Verification Failed
- ✅ Secret matches in both DCSServerBot and Loggers config
- ✅ No extra spaces in secret
- ✅ X-DCS-Signature header being sent

### Data Not Processing
- ✅ Check Loggers backend logs for errors
- ✅ Verify required fields in webhook data
- ✅ Ensure Loggers backend is accessible

## 📁 File Locations Summary

| File | Source | Destination |
|------|--------|-------------|
| `userstats.yaml` | `backend/dcs_bot_configs/` | `YourDCSServerBot/plugins/` |
| `missionstats.yaml` | `backend/dcs_bot_configs/` | `YourDCSServerBot/plugins/` |
| Environment vars | `backend/dcs_bot_configs/loggers_env_snippet.txt` | `backend/.env` |

## 🔐 Security Notes

- Keep `loggers_webhook_secret_2024` secure
- Use HTTPS in production
- Consider firewall rules for webhook endpoints
- Update DCSServerBot regularly

## 📞 Need Help?

1. Check the detailed documentation: `backend/DCS_BOT_README.md`
2. Run the test script: `python backend/test_dcs_bot.py`
3. Check logs in both DCSServerBot and Loggers backend
4. Verify network connectivity between services

---

**🎉 You're all set!** Once configured, your DCS missions will automatically update pilot profiles in real-time through the Loggers integration. 