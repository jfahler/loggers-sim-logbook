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
  maxAltitudeFeet?: number;
  maxSpeedKnots?: number;
  distanceNm?: number;
  kills: number;
  deaths: number;
  tacviewFilename?: string;
  createdAt: Date;
}

export interface FlightEvent {
  id: number;
  flightId: number;
  eventType: string;
  eventTime: Date;
  description?: string;
  targetName?: string;
  weaponUsed?: string;
  createdAt: Date;
}

export interface FlightSummary extends Flight {
  pilotName: string;
  pilotCallsign?: string;
  events: FlightEvent[];
}

export interface PilotStats {
  pilot: Pilot;
  totalFlights: number;
  totalFlightTime: number;
  totalKills: number;
  totalDeaths: number;
  favoriteAircraft: string;
  averageFlightDuration: number;
}
