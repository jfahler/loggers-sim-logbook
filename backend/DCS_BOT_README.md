# DCS Server Bot Integration

This document describes the integration between the Loggers DCS Squadron Logbook and [DCSServerBot](https://github.com/Special-K-s-Flightsim-Bots/DCSServerBot), specifically focusing on the USERSTATS and MISSIONSTATS plugins.

## Overview

The DCS Server Bot integration provides real-time data processing from DCS missions, allowing for immediate updates to pilot profiles and mission statistics without requiring manual Tacview XML file uploads.

### Benefits

- **Real-time Updates**: Pilot statistics are updated immediately after each mission
- **Enhanced Security**: Webhook signature verification ensures data integrity
- **Automatic Processing**: No manual intervention required for data collection
- **Discord Integration**: Automatic Discord notifications for mission events
- **Comprehensive Logging**: Detailed operation logging for debugging and monitoring

## Supported Plugins

### USERSTATS Plugin

The USERSTATS plugin integration processes individual player statistics from DCS missions:

- **Player Information**: Name, UCID, player ID
- **Mission Data**: Mission name, server name, aircraft type
- **Flight Statistics**: Flight time, kills (air/ground/friendly), deaths, ejections
- **Real-time Updates**: Immediate profile updates after each mission

### MISSIONSTATS Plugin

The MISSIONSTATS plugin integration processes complete mission summaries:

- **Mission Overview**: Mission name, duration, start/end times
- **Player Participation**: All players and their individual statistics
- **Mission Statistics**: Aggregate mission data and performance metrics
- **Mission Files**: Automatic generation of mission summary files

## Configuration

### Environment Variables

Add the following variables to your `.env` file:

```env
# DCS Server Bot Integration
DCS_BOT_ENABLED=true
DCS_BOT_WEBHOOK_SECRET=your_webhook_secret_here
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `DCS_BOT_ENABLED` | `false` | Enable/disable DCS Bot integration |
| `DCS_BOT_WEBHOOK_SECRET` | `""` | Secret key for webhook signature verification |

## DCSServerBot Configuration

### USERSTATS Plugin Setup

1. **Install USERSTATS Plugin**:
   ```bash
   # In your DCSServerBot installation
   ./update.py -y
   ```

2. **Configure USERSTATS Plugin**:
   ```yaml
   # In your plugins/userstats.yaml
   userstats:
     webhook_url: "http://your-server:5000/dcs/userstats"
     webhook_secret: "your_webhook_secret_here"
     enabled: true
   ```

3. **Webhook Configuration**:
   - **URL**: `http://your-server:5000/dcs/userstats`
   - **Method**: POST
   - **Content-Type**: application/json
   - **Headers**: Include `X-DCS-Signature` for verification

### MISSIONSTATS Plugin Setup

1. **Install MISSIONSTATS Plugin**:
   ```bash
   # In your DCSServerBot installation
   ./update.py -y
   ```

2. **Configure MISSIONSTATS Plugin**:
   ```yaml
   # In your plugins/missionstats.yaml
   missionstats:
     webhook_url: "http://your-server:5000/dcs/missionstats"
     webhook_secret: "your_webhook_secret_here"
     enabled: true
   ```

3. **Webhook Configuration**:
   - **URL**: `http://your-server:5000/dcs/missionstats`
   - **Method**: POST
   - **Content-Type**: application/json
   - **Headers**: Include `X-DCS-Signature` for verification

## API Endpoints

### USERSTATS Webhook

**Endpoint**: `POST /dcs/userstats`

**Headers**:
```
Content-Type: application/json
X-DCS-Signature: your_signature_here
```

**Request Body**:
```json
{
  "player_name": "PilotName",
  "player_ucid": "pilot_ucid_12345",
  "player_id": 12345,
  "server_name": "DCS Server Name",
  "mission_name": "Operation Mission",
  "mission_id": "mission_001",
  "flight_time": 3600,
  "kills": {
    "air": 2,
    "ground": 3,
    "friendly": 0
  },
  "deaths": 1,
  "ejections": 0,
  "crashes": 0,
  "aircraft_type": "F-16C",
  "side": "blue",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Response**:
```json
{
  "success": true,
  "message": "USERSTATS processed successfully",
  "request_id": "uuid-here",
  "player_name": "PilotName",
  "total_kills": 5,
  "flight_time": 3600
}
```

### MISSIONSTATS Webhook

**Endpoint**: `POST /dcs/missionstats`

**Headers**:
```
Content-Type: application/json
X-DCS-Signature: your_signature_here
```

**Request Body**:
```json
{
  "mission_name": "Operation Mission",
  "mission_id": "mission_001",
  "server_name": "DCS Server Name",
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T12:00:00Z",
  "duration": 7200,
  "players": [
    {
      "name": "Pilot1",
      "ucid": "pilot1_ucid",
      "flight_time": 3600,
      "kills": {"air": 2, "ground": 1},
      "deaths": 1,
      "ejections": 0,
      "aircraft": "F-16C"
    }
  ],
  "statistics": {
    "total_kills": 6,
    "total_deaths": 1,
    "total_flight_time": 5400,
    "aircraft_used": ["F-16C", "F/A-18C"]
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "MISSIONSTATS processed successfully",
  "request_id": "uuid-here",
  "mission_name": "Operation Mission",
  "players_count": 2,
  "duration": 7200,
  "mission_file": "mission_001_1704110400.json"
}
```

## Security Features

### Webhook Signature Verification

The integration includes webhook signature verification to ensure data integrity:

1. **Secret Configuration**: Set `DCS_BOT_WEBHOOK_SECRET` in your environment
2. **Signature Header**: DCSServerBot sends `X-DCS-Signature` header
3. **Verification**: The system verifies the signature before processing data
4. **Fallback**: If no secret is configured, all requests are accepted (for testing)

### Rate Limiting

Webhook endpoints are rate-limited to prevent abuse:

- **USERSTATS**: 30 requests per minute
- **MISSIONSTATS**: 30 requests per minute

### Input Validation

All incoming data is validated and sanitized:

- **Required Fields**: Ensures all required data is present
- **Data Types**: Validates data types and formats
- **String Sanitization**: Removes dangerous characters
- **Size Limits**: Prevents oversized payloads

## Testing

### Test Script

Use the provided test script to verify the integration:

```bash
cd backend
python test_dcs_bot.py
```

### Manual Testing

Test the endpoints manually using curl:

```bash
# Test USERSTATS endpoint
curl -X POST http://localhost:5000/dcs/userstats \
  -H "Content-Type: application/json" \
  -H "X-DCS-Signature: test_signature" \
  -d '{
    "player_name": "TestPilot",
    "player_ucid": "test_ucid",
    "server_name": "Test Server",
    "mission_name": "Test Mission",
    "flight_time": 3600,
    "kills": {"air": 1, "ground": 2},
    "deaths": 0,
    "aircraft_type": "F-16C"
  }'

# Test MISSIONSTATS endpoint
curl -X POST http://localhost:5000/dcs/missionstats \
  -H "Content-Type: application/json" \
  -H "X-DCS-Signature: test_signature" \
  -d '{
    "mission_name": "Test Mission",
    "server_name": "Test Server",
    "start_time": "2024-01-01T10:00:00Z",
    "players": []
  }'
```

## Monitoring

### Health Check

Monitor the integration status via the health endpoint:

```bash
curl http://localhost:5000/health
```

Response includes DCS Bot status:
```json
{
  "status": "healthy",
  "dcs_bot_enabled": true,
  "dcs_bot_webhook_configured": true
}
```

### Error Statistics

Monitor error rates via the error statistics endpoint:

```bash
curl http://localhost:5000/error-stats
```

### Logging

The integration provides comprehensive logging:

- **Operation Logging**: Start, success, and failure events
- **Request Tracking**: Unique request IDs for debugging
- **Error Details**: Detailed error information with context
- **Performance Metrics**: Processing times and statistics

## Troubleshooting

### Common Issues

1. **Webhook Not Receiving Data**:
   - Check if `DCS_BOT_ENABLED=true` in environment
   - Verify DCSServerBot webhook configuration
   - Check network connectivity and firewall settings

2. **Signature Verification Failed**:
   - Ensure `DCS_BOT_WEBHOOK_SECRET` matches DCSServerBot configuration
   - Check that `X-DCS-Signature` header is being sent

3. **Data Not Processing**:
   - Check server logs for validation errors
   - Verify required fields are present in webhook data
   - Ensure data formats match expected schema

4. **Rate Limiting**:
   - Check if you're hitting rate limits (30 requests/minute)
   - Monitor error statistics for rate limit errors

### Debug Mode

Enable debug logging by setting `FLASK_DEBUG=True` in your environment:

```env
FLASK_DEBUG=True
```

### Log Files

Check the application logs for detailed information:

```bash
tail -f backend/app.log
```

## Integration with Existing Features

### Pilot Profiles

USERSTATS data automatically updates pilot profiles:

- **Flight Time**: Accumulated flight time tracking
- **Kill Statistics**: Air-to-air, air-to-ground, and friendly kills
- **Mission History**: Complete mission participation records
- **Aircraft Usage**: Preferred aircraft tracking

### Discord Integration

When Discord webhook is configured, the integration sends:

- **Flight Summaries**: Individual flight statistics after each mission
- **Mission Updates**: Real-time mission progress updates
- **Achievement Notifications**: Special achievements and milestones

### Data Export

Mission statistics are automatically saved to files:

- **Location**: `backend/uploads/` directory
- **Format**: JSON files with timestamp
- **Content**: Complete mission data and player statistics
- **Naming**: `mission_{id}_{timestamp}.json`

## Best Practices

### Security

1. **Use Strong Secrets**: Generate strong webhook secrets
2. **Network Security**: Use HTTPS in production
3. **Firewall Rules**: Restrict access to webhook endpoints
4. **Regular Updates**: Keep DCSServerBot updated

### Performance

1. **Monitor Rate Limits**: Stay within rate limit thresholds
2. **Database Optimization**: Regular cleanup of old data
3. **Log Rotation**: Implement log rotation for large deployments
4. **Resource Monitoring**: Monitor CPU and memory usage

### Maintenance

1. **Regular Testing**: Run test scripts regularly
2. **Backup Data**: Regular backups of pilot profiles
3. **Update Dependencies**: Keep Python packages updated
4. **Monitor Logs**: Regular log review for issues

## Support

For issues with the DCS Server Bot integration:

1. **Check Logs**: Review application logs for error details
2. **Test Scripts**: Run test scripts to isolate issues
3. **DCSServerBot Documentation**: Refer to [DCSServerBot documentation](https://github.com/Special-K-s-Flightsim-Bots/DCSServerBot)
4. **Community Support**: Check DCSServerBot Discord for community help

## References

- [DCSServerBot GitHub Repository](https://github.com/Special-K-s-Flightsim-Bots/DCSServerBot)
- [USERSTATS Plugin Documentation](https://github.com/Special-K-s-Flightsim-Bots/DCSServerBot/blob/master/plugins/userstats/README.md)
- [MISSIONSTATS Plugin Documentation](https://github.com/Special-K-s-Flightsim-Bots/DCSServerBot/blob/master/plugins/missionstats/README.md)
- [DCSServerBot Web Documentation](https://special-k-s-flightsim-bots.github.io/DCSServerBot/) 