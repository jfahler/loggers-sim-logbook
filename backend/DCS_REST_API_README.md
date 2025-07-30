# DCS Server Bot REST API Integration

This document describes the integration between the Loggers DCS Squadron Logbook and [DCSServerBot's REST API plugin](https://github.com/Special-K-s-Flightsim-Bots/DCSServerBot/tree/master/plugins/restapi), providing additional server management and monitoring capabilities.

## Overview

The DCS REST API integration extends the existing DCS Server Bot integration by adding real-time server management capabilities, including:

- **Server Information**: Get current server status, mission details, and player counts
- **Player Management**: View connected players, kick/ban players, and get player statistics
- **Mission Control**: Restart missions, load new missions, and get mission information
- **Chat Integration**: Send messages to the DCS server chat
- **Server Statistics**: Get comprehensive server performance metrics

### Benefits

- **Real-time Monitoring**: Live server status and player information
- **Server Management**: Administrative controls for mission and player management
- **Enhanced Integration**: Seamless integration with existing DCS Bot webhooks
- **Security**: Token-based authentication and rate limiting
- **Comprehensive Logging**: Detailed operation logging for debugging and monitoring

## Configuration

### Environment Variables

Add the following variables to your `.env` file:

```env
# DCS REST API Integration
DCS_REST_API_ENABLED=true
DCS_REST_API_URL=http://localhost:8080
DCS_REST_API_TOKEN=loggers_rest_api_token_2024
DCS_REST_API_TIMEOUT=30
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `DCS_REST_API_ENABLED` | `false` | Enable/disable DCS REST API integration |
| `DCS_REST_API_URL` | `http://localhost:8080` | DCS Server Bot REST API URL |
| `DCS_REST_API_TOKEN` | `""` | Authentication token for REST API |
| `DCS_REST_API_TIMEOUT` | `30` | Request timeout in seconds |

## DCSServerBot Configuration

### REST API Plugin Setup

1. **Install REST API Plugin**:
   ```bash
   # In your DCSServerBot installation
   ./update.py -y
   ```

2. **Configure REST API Plugin**:
   ```yaml
   # In your plugins/restapi.yaml
   restapi:
     enabled: true
     port: 8080
     host: "0.0.0.0"
     token: "loggers_rest_api_token_2024"
     cors_origins: ["http://localhost:3000", "http://localhost:5000"]
     rate_limit: 100
     rate_limit_window: 60
     
     # Authentication
     auth_required: true
     token_header: "Authorization"
     token_prefix: "Bearer"
     
     # Endpoints to enable
     endpoints:
       server_info: true
       server_players: true
       server_mission: true
       server_chat: true
       server_restart: true
       server_missions: true
       server_stats: true
       player_kick: true
       player_ban: true
       player_unban: true
   ```

3. **Restart DCSServerBot**:
   ```bash
   cd YourDCSServerBot
   ./restart.py
   ```

## API Endpoints

### Server Information

**Endpoint**: `GET /dcs/server/info`

**Response**:
```json
{
  "success": true,
  "server": {
    "name": "DCS Server Name",
    "mission_name": "Operation Mission",
    "mission_start_time": "2024-01-01T10:00:00Z",
    "players_count": 5,
    "max_players": 20,
    "status": "running",
    "version": "2.9.0"
  },
  "request_id": "uuid-here"
}
```

### Server Players

**Endpoint**: `GET /dcs/server/players`

**Response**:
```json
{
  "success": true,
  "players": [
    {
      "name": "PilotName",
      "ucid": "pilot_ucid_12345",
      "id": 12345,
      "side": "blue",
      "slot": "F-16C #001",
      "unit_type": "F-16C",
      "unit_name": "F-16C #001",
      "group_id": 1,
      "ping": 45,
      "connected_at": "2024-01-01T10:30:00Z"
    }
  ],
  "count": 1,
  "request_id": "uuid-here"
}
```

### Player Information

**Endpoint**: `GET /dcs/server/players/<player_id>`

**Response**:
```json
{
  "success": true,
  "player": {
    "name": "PilotName",
    "ucid": "pilot_ucid_12345",
    "id": 12345,
    "side": "blue",
    "slot": "F-16C #001",
    "unit_type": "F-16C",
    "unit_name": "F-16C #001",
    "group_id": 1,
    "ping": 45,
    "connected_at": "2024-01-01T10:30:00Z"
  },
  "request_id": "uuid-here"
}
```

### Mission Information

**Endpoint**: `GET /dcs/server/mission`

**Response**:
```json
{
  "success": true,
  "mission": {
    "name": "Operation Mission",
    "description": "Mission description",
    "theatre": "Caucasus",
    "start_time": "2024-01-01T10:00:00Z",
    "duration": 7200,
    "weather": {
      "clouds": "scattered",
      "visibility": 10000
    },
    "briefing": "Mission briefing text"
  },
  "request_id": "uuid-here"
}
```

### Send Chat Message

**Endpoint**: `POST /dcs/server/chat`

**Request Body**:
```json
{
  "message": "Welcome to the server!",
  "coalition": "all"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Chat message sent successfully",
  "request_id": "uuid-here"
}
```

### Restart Mission

**Endpoint**: `POST /dcs/server/mission/restart`

**Response**:
```json
{
  "success": true,
  "message": "Mission restarted successfully",
  "request_id": "uuid-here"
}
```

### Available Missions

**Endpoint**: `GET /dcs/server/missions`

**Response**:
```json
{
  "success": true,
  "missions": [
    "Operation Mission.miz",
    "Training Mission.miz",
    "Campaign Mission.miz"
  ],
  "count": 3,
  "request_id": "uuid-here"
}
```

### Server Statistics

**Endpoint**: `GET /dcs/server/stats`

**Response**:
```json
{
  "success": true,
  "stats": {
    "uptime": 3600,
    "total_players": 25,
    "current_players": 5,
    "missions_played": 10,
    "total_flight_time": 18000
  },
  "request_id": "uuid-here"
}
```

## Authentication

All REST API endpoints require authentication using a Bearer token:

```bash
curl -H "Authorization: Bearer loggers_rest_api_token_2024" \
     http://localhost:5000/dcs/server/info
```

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "DCS_REST_API_ERROR",
    "message": "Error description",
    "status_code": 500
  },
  "request_id": "uuid-here"
}
```

### Common Error Codes

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| `DCS_REST_API_DISABLED` | REST API integration disabled | 503 |
| `DCS_REST_API_ERROR` | General REST API error | 500 |
| `DCS_REST_API_TIMEOUT` | Request timeout | 408 |
| `DCS_REST_API_AUTH_ERROR` | Authentication failed | 401 |

## Security Features

### Rate Limiting

REST API endpoints are rate-limited to prevent abuse:

- **Default**: 100 requests per minute (general endpoints)
- **Configurable**: Adjust via environment variables

### Input Validation

All incoming data is validated and sanitized:

- **Required Fields**: Ensures all required data is present
- **Data Types**: Validates data types and formats
- **String Sanitization**: Removes dangerous characters
- **Size Limits**: Prevents oversized payloads

### Token Authentication

- **Bearer Token**: Required for all endpoints
- **Configurable**: Token can be changed via environment variables
- **Secure**: Tokens should be kept secure and rotated regularly

## Testing

### Test Script

Create a test script to verify the integration:

```bash
#!/bin/bash

# Test server info
echo "Testing server info..."
curl -H "Authorization: Bearer loggers_rest_api_token_2024" \
     http://localhost:5000/dcs/server/info

# Test players list
echo -e "\nTesting players list..."
curl -H "Authorization: Bearer loggers_rest_api_token_2024" \
     http://localhost:5000/dcs/server/players

# Test chat message
echo -e "\nTesting chat message..."
curl -X POST -H "Authorization: Bearer loggers_rest_api_token_2024" \
     -H "Content-Type: application/json" \
     -d '{"message": "Test message from Loggers"}' \
     http://localhost:5000/dcs/server/chat
```

### Manual Testing

Test endpoints manually using curl:

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

## Monitoring

### Health Check

Monitor the integration status via the health endpoint:

```bash
curl http://localhost:5000/health
```

Response includes REST API status:
```json
{
  "status": "healthy",
  "dcs_bot_enabled": true,
  "dcs_rest_api_enabled": true,
  "dcs_rest_api_configured": true
}
```

### Logging

REST API operations are logged with detailed information:

- **Request Details**: Method, endpoint, parameters
- **Response Status**: Success/failure, status codes
- **Error Information**: Detailed error messages and stack traces
- **Performance Metrics**: Request duration and timing

## Integration with Existing Features

### Combined with Webhooks

The REST API integration works alongside the existing webhook integration:

1. **Real-time Data**: Webhooks provide real-time mission and player data
2. **Server Management**: REST API provides server control and monitoring
3. **Unified Interface**: Both integrations use the same authentication and error handling

### Frontend Integration

The REST API endpoints can be integrated into the frontend:

- **Server Status Dashboard**: Real-time server information
- **Player Management**: View and manage connected players
- **Mission Control**: Mission restart and loading capabilities
- **Chat Integration**: Send messages to the server

## Best Practices

### Security

1. **Use Strong Tokens**: Generate strong authentication tokens
2. **Network Security**: Use HTTPS in production
3. **Firewall Rules**: Restrict access to REST API endpoints
4. **Regular Updates**: Keep DCSServerBot updated

### Performance

1. **Monitor Rate Limits**: Stay within rate limit thresholds
2. **Connection Pooling**: Reuse HTTP connections when possible
3. **Timeout Configuration**: Set appropriate timeouts for your network
4. **Resource Monitoring**: Monitor CPU and memory usage

### Maintenance

1. **Regular Testing**: Run test scripts regularly
2. **Log Review**: Regular log review for issues
3. **Token Rotation**: Rotate authentication tokens periodically
4. **Update Dependencies**: Keep Python packages updated

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if DCSServerBot REST API is running
   - Verify port configuration (default: 8080)
   - Check firewall settings

2. **Authentication Failed**
   - Verify token matches in both configurations
   - Check token format (Bearer prefix)
   - Ensure token is not expired

3. **Timeout Errors**
   - Increase timeout value in configuration
   - Check network connectivity
   - Verify server resources

4. **Rate Limit Exceeded**
   - Reduce request frequency
   - Increase rate limit in configuration
   - Implement request caching

### Debug Mode

Enable debug logging for troubleshooting:

```env
DCS_REST_API_DEBUG=true
```

## References

- [DCSServerBot GitHub Repository](https://github.com/Special-K-s-Flightsim-Bots/DCSServerBot)
- [REST API Plugin Documentation](https://github.com/Special-K-s-Flightsim-Bots/DCSServerBot/tree/master/plugins/restapi)
- [DCSServerBot Web Documentation](https://special-k-s-flightsim-bots.github.io/DCSServerBot/)
- [DCS Server Bot Integration README](DCS_BOT_README.md) 