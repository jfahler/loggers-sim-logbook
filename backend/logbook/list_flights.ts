import { api } from "encore.dev/api";
import { Query } from "encore.dev/api";
import { logbookDB } from "./db";
import type { FlightSummary } from "./types";

export interface ListFlightsRequest {
  pilotId?: Query<number>;
  limit?: Query<number>;
  offset?: Query<number>;
}

export interface ListFlightsResponse {
  flights: FlightSummary[];
  total: number;
}

// Retrieves all flights with pilot information and events.
export const listFlights = api<ListFlightsRequest, ListFlightsResponse>(
  { expose: true, method: "GET", path: "/flights" },
  async (req) => {
    const limit = req.limit || 50;
    const offset = req.offset || 0;
    
    let whereClause = "";
    let params: any[] = [];
    
    if (req.pilotId) {
      whereClause = "WHERE f.pilot_id = $1";
      params.push(req.pilotId);
    }

    const flights = await logbookDB.queryAll<any>`
      SELECT 
        f.id, f.pilot_id, f.aircraft_type, f.mission_name,
        f.start_time, f.end_time, f.duration_seconds,
        f.max_altitude_feet, f.max_speed_knots, f.distance_nm,
        f.kills, f.deaths, f.tacview_filename, f.created_at,
        p.name as pilot_name, p.callsign as pilot_callsign
      FROM flights f
      JOIN pilots p ON f.pilot_id = p.id
      ${whereClause ? `WHERE f.pilot_id = ${req.pilotId}` : ''}
      ORDER BY f.start_time DESC
      LIMIT ${limit} OFFSET ${offset}
    `;

    const total = await logbookDB.queryRow<{ count: number }>`
      SELECT COUNT(*) as count FROM flights f
      ${whereClause ? `WHERE f.pilot_id = ${req.pilotId}` : ''}
    `;

    const flightSummaries: FlightSummary[] = [];

    for (const flight of flights) {
      const events = await logbookDB.queryAll<any>`
        SELECT id, flight_id, event_type, event_time, description, target_name, weapon_used, created_at
        FROM flight_events
        WHERE flight_id = ${flight.id}
        ORDER BY event_time ASC
      `;

      flightSummaries.push({
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
      });
    }

    return {
      flights: flightSummaries,
      total: total?.count || 0
    };
  }
);
