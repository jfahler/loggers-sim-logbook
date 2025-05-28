import { api, APIError } from "encore.dev/api";
import { logbookDB } from "./db";
import type { FlightSummary } from "./types";

export interface GetFlightRequest {
  id: number;
}

// Retrieves a specific flight with all details.
export const getFlight = api<GetFlightRequest, FlightSummary>(
  { expose: true, method: "GET", path: "/flights/:id" },
  async (req) => {
    const flight = await logbookDB.queryRow<any>`
      SELECT 
        f.id, f.pilot_id, f.aircraft_type, f.mission_name,
        f.start_time, f.end_time, f.duration_seconds,
        f.aa_kills, f.ag_kills, f.frat_kills, f.rtb_count,
        f.ejections, f.deaths, f.tacview_filename, f.created_at,
        p.name as pilot_name, p.callsign as pilot_callsign
      FROM flights f
      JOIN pilots p ON f.pilot_id = p.id
      WHERE f.id = ${req.id}
    `;

    if (!flight) {
      throw APIError.notFound("flight not found");
    }

    return {
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
    };
  }
);
