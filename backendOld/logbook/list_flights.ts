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

// Retrieves all flights with pilot information.
export const listFlights = api<ListFlightsRequest, ListFlightsResponse>(
  { expose: true, method: "GET", path: "/flights" },
  async (req) => {
    const limit = req.limit || 50;
    const offset = req.offset || 0;

    let flights;
    let total;

    if (req.pilotId) {
      flights = await logbookDB.queryAll<any>`
        SELECT 
          f.id, f.pilot_id, f.aircraft_type, f.mission_name,
          f.start_time, f.end_time, f.duration_seconds,
          f.aa_kills, f.ag_kills, f.frat_kills, f.rtb_count,
          f.ejections, f.deaths, f.tacview_filename, f.created_at,
          p.name as pilot_name, p.callsign as pilot_callsign
        FROM flights f
        JOIN pilots p ON f.pilot_id = p.id
        WHERE f.pilot_id = ${req.pilotId}
        ORDER BY f.start_time DESC
        LIMIT ${limit} OFFSET ${offset}
      `;

      total = await logbookDB.queryRow<{ count: number }>`
        SELECT COUNT(*) as count FROM flights f
        WHERE f.pilot_id = ${req.pilotId}
      `;
    } else {
      flights = await logbookDB.queryAll<any>`
        SELECT 
          f.id, f.pilot_id, f.aircraft_type, f.mission_name,
          f.start_time, f.end_time, f.duration_seconds,
          f.aa_kills, f.ag_kills, f.frat_kills, f.rtb_count,
          f.ejections, f.deaths, f.tacview_filename, f.created_at,
          p.name as pilot_name, p.callsign as pilot_callsign
        FROM flights f
        JOIN pilots p ON f.pilot_id = p.id
        ORDER BY f.start_time DESC
        LIMIT ${limit} OFFSET ${offset}
      `;

      total = await logbookDB.queryRow<{ count: number }>`
        SELECT COUNT(*) as count FROM flights f
      `;
    }

    const flightSummaries: FlightSummary[] = flights.map(flight => ({
      id: flight.id,
      pilotId: flight.pilot_id,
      aircraftType: flight.aircraft_type,
      missionName: flight.mission_name,
      startTime: flight.start_time,
      endTime: flight.end_time,
      durationSeconds: flight.duration_seconds,
      aaKills: flight.aa_kills,
      agKills: flight.ag_kills,
      fratKills: flight.frat_kills,
      rtbCount: flight.rtb_count,
      ejections: flight.ejections,
      deaths: flight.deaths,
      tacviewFilename: flight.tacview_filename,
      createdAt: flight.created_at,
      pilotName: flight.pilot_name,
      pilotCallsign: flight.pilot_callsign
    }));

    return {
      flights: flightSummaries,
      total: total?.count || 0
    };
  }
);
