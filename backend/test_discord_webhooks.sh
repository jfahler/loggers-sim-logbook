#!/bin/bash

echo "🎯 Testing /discord/pilot-stats..."
curl -X POST http://localhost:5000/discord/pilot-stats \
  -H "Content-Type: application/json" \
  -d '{
    "pilotName": "DrunkBonsai",
    "pilotCallsign": "Drunk1",
    "totalFlights": 12,
    "totalFlightTime": 9823,
    "averageFlightDuration": 818,
    "totalAaKills": 5,
    "totalAgKills": 4,
    "totalFratKills": 0,
    "totalRtbCount": 9,
    "totalEjections": 1,
    "totalDeaths": 2,
    "favoriteAircraft": "F-16C"
}'

echo -e "\n✅ Pilot stats sent."

echo -e "\n🛫 Testing /discord/flight-summary..."
curl -X POST http://localhost:5000/discord/flight-summary \
  -H "Content-Type: application/json" \
  -d '{
    "flightId": 42,
    "pilotName": "DrunkBonsai",
    "pilotCallsign": "Drunk1",
    "aircraftType": "F-16C",
    "missionName": "Operation Fireline",
    "startTime": "2025-06-03T23:00:00Z",
    "durationSeconds": 2730,
    "aaKills": 1,
    "agKills": 3,
    "fratKills": 0,
    "rtbCount": 1,
    "ejections": 0,
    "deaths": 0
}'

echo -e "\n✅ Flight summary sent."
echo "🚀 All done. Check your Discord channel!"

