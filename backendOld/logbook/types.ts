export interface Pilot {
  id: number;
  name: string;
  callsign?: string;
  createdAt: Date;
}

export interface Flight {
  id: number;
  pilotId: number;
  aircraftType: string;
  missionName?: string;
  startTime: Date;
  endTime?: Date;
  durationSeconds?: number;
  aaKills: number;
  agKills: number;
  fratKills: number;
  rtbCount: number;
  ejections: number;
  deaths: number;
  tacviewFilename?: string;
  createdAt: Date;
}

export interface FlightSummary extends Flight {
  pilotName: string;
  pilotCallsign?: string;
}

export interface PilotStats {
  pilot: Pilot;
  totalFlights: number;
  totalFlightTime: number;
  totalAaKills: number;
  totalAgKills: number;
  totalFratKills: number;
  totalRtbCount: number;
  totalEjections: number;
  totalDeaths: number;
  favoriteAircraft: string;
  averageFlightDuration: number;
}
