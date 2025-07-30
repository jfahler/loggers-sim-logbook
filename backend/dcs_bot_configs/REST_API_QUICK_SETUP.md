# 🚀 Quick Setup: DCS REST API Integration

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

This installs the REST API plugin.

### Step 3: Copy Configuration Files

Copy these files to your DCSServerBot `plugins/` directory:

**From:** `backend/dcs_bot_configs/restapi.yaml`
**To:** `YourDCSServerBot/plugins/restapi.yaml`

### Step 4: Configure Loggers Backend

Add these lines to your Loggers backend `.env` file:
```env
DCS_REST_API_ENABLED=true
DCS_REST_API_URL=http://localhost:8080
DCS_REST_API_TOKEN=loggers_rest_api_token_2024
DCS_REST_API_TIMEOUT=30
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

Run the test script:
```bash
cd backend
python test_dcs_rest_api.py
```

## 🧪 Manual Testing

Test the endpoints manually:

```bash
# Get server information
curl -H "Authorization: Bearer loggers_rest_api_token_2024" \
     http://localhost:5000/dcs/server/info

# Get current players
curl -H "Authorization: Bearer loggers_rest_api_token_2024" \
     http://localhost:5000/dcs/server/players

# Send chat message
curl -X POST -H "Authorization: Bearer loggers_rest_api_token_2024" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello from Loggers!", "coalition": "all"}' \
     http://localhost:5000/dcs/server/chat
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
  "dcs_rest_api_enabled": true,
  "dcs_rest_api_configured": true
}
```

## 🚨 Troubleshooting

### REST API Not Responding
- ✅ DCSServerBot running? `./status.py`
- ✅ REST API plugin enabled? Check `plugins/restapi.yaml`
- ✅ Port 8080 accessible? Test with `curl http://localhost:8080`
- ✅ Loggers backend running? Check `http://localhost:5000/health`

### Authentication Failed
- ✅ Token matches in both DCSServerBot and Loggers config
- ✅ Bearer prefix included in Authorization header
- ✅ No extra spaces in token

### Connection Refused
- ✅ Check if REST API is running on port 8080
- ✅ Verify firewall settings
- ✅ Ensure DCSServerBot has permission to bind to port

## 📁 File Locations Summary

| File | Source | Destination |
|------|--------|-------------|
| `restapi.yaml` | `backend/dcs_bot_configs/` | `YourDCSServerBot/plugins/` |
| Environment vars | `backend/dcs_bot_configs/loggers_env_restapi.txt` | `backend/.env` |

## 🔐 Security Notes

- Keep `loggers_rest_api_token_2024` secure
- Use HTTPS in production
- Restrict access to REST API endpoints
- Rotate tokens regularly

## 📚 Next Steps

1. **Test all endpoints** using the test script
2. **Integrate with frontend** for server management
3. **Set up monitoring** for REST API health
4. **Configure alerts** for server events

## 📞 Need Help?

1. **Check Loggers backend logs** for error details
2. **Review DCSServerBot logs** for REST API issues
3. **Run test script** to isolate problems
4. **Check network connectivity** between services 