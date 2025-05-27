import { api, APIError } from "encore.dev/api";
import { logbookDB } from "./db";
import type { FlightSummary } from "./types";

export interface GetFlightRequest {
  id: number;
}

// Retrieves a specific flight with all details and events.
export const getFlight = api<GetFlightRequest, FlightSummary>(
  { expose: true, method: "GET", path: "/flights/:id" },
  async (req) => {
    const flight = await logbookDB.queryRow<any>`
      SELECT 
        f.id, f.pilot_id, f.aircraft_type, f.mission_name,
        f.start_time, f.end_time, f.duration_seconds,
        f.max_altitude_feet, f.max_speed_knots, f.distance_nm,
        f.kills, f.deaths, f.tacview_filename, f.created_at,
        p.name as pilot_name, p.callsign as pilot_callsign
      FROM flights f
      JOIN pilots p ON f.pilot_id = p.id
      WHERE f.id = ${req.id}
    `;

    if (!flight) {
      throw APIError.notFound("flight not found");
    }

    const events = await logbookDB.queryAll<any>`
      SELECT id, flight_id, event_type, event_time, description, target_name, weapon_used, created_at
      FROM flight_events
      WHERE flight_id = ${req.id}
      ORDER BY event_time ASC
    `;

    return {
      id: flight.id,
      pilotId: flight.pilot_id,
      aircraftType: flight.aircraft_type,
      missionName: flight.mission_name,
      startTime: flight.start_time,
      endTime: flight.end_time,
      durationSeconds: flight.duration_seconds,
      maxAltitudeFeet: flight.max_altitude_feet,
      maxSpeedKnots: flight.max_speed_knots,
      distanceNm: flight.distance_nm,
      kills: flight.kills,
      deaths: flight.deaths,
      tacviewFilename: flight.tacview_filename,
      createdAt: flight.created_at,
      pilotName: flight.pilot_name,
      pilotCallsign: flight.pilot_callsign,
      events: events.map(e => ({
        id: e.id,
        flightId: e.flight_id,
        eventType: e.event_type,
        eventTime: e.event_time,
        description: e.description,
        targetName: e.target_name,
        weaponUsed: e.weapon_used,
        createdAt: e.created_at
      }))
    };
  }
);
