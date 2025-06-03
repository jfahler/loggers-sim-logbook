import { api } from "encore.dev/api";
import { logbookDB } from "./db";
import type { PilotStats } from "./types";

export interface ListPilotsResponse {
  pilots: PilotStats[];
}

// Retrieves all pilots with their statistics.
export const listPilots = api<void, ListPilotsResponse>(
  { expose: true, method: "GET", path: "/pilots" },
  async () => {
    const pilots = await logbookDB.queryAll<any>`
      SELECT 
        p.id, p.name, p.callsign, p.created_at,
        COUNT(f.id) as total_flights,
        COALESCE(SUM(f.duration_seconds), 0) as total_flight_time,
        COALESCE(SUM(f.aa_kills), 0) as total_aa_kills,
        COALESCE(SUM(f.ag_kills), 0) as total_ag_kills,
        COALESCE(SUM(f.frat_kills), 0) as total_frat_kills,
        COALESCE(SUM(f.rtb_count), 0) as total_rtb_count,
        COALESCE(SUM(f.ejections), 0) as total_ejections,
        COALESCE(SUM(f.deaths), 0) as total_deaths,
        COALESCE(AVG(f.duration_seconds)::INTEGER, 0) as average_flight_duration
      FROM pilots p
      LEFT JOIN flights f ON p.id = f.pilot_id
      GROUP BY p.id, p.name, p.callsign, p.created_at
      ORDER BY total_flights DESC, p.name ASC
    `;

    const pilotStats: PilotStats[] = [];

    for (const pilot of pilots) {
      // Get favorite aircraft
      const favoriteAircraft = await logbookDB.queryRow<{ aircraft_type: string }>`
        SELECT aircraft_type
        FROM flights
        WHERE pilot_id = ${pilot.id}
        GROUP BY aircraft_type
        ORDER BY COUNT(*) DESC
        LIMIT 1
      `;

      pilotStats.push({
        pilot: {
          id: pilot.id,
          name: pilot.name,
          callsign: pilot.callsign,
          createdAt: pilot.created_at
        },
        totalFlights: pilot.total_flights,
        totalFlightTime: pilot.total_flight_time,
        totalAaKills: pilot.total_aa_kills,
        totalAgKills: pilot.total_ag_kills,
        totalFratKills: pilot.total_frat_kills,
        totalRtbCount: pilot.total_rtb_count,
        totalEjections: pilot.total_ejections,
        totalDeaths: pilot.total_deaths,
        favoriteAircraft: favoriteAircraft?.aircraft_type || 'None',
        averageFlightDuration: pilot.average_flight_duration
      });
    }

    return { pilots: pilotStats };
  }
);
