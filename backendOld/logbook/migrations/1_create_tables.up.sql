CREATE TABLE pilots (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  callsign TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE flights (
  id BIGSERIAL PRIMARY KEY,
  pilot_id BIGINT NOT NULL REFERENCES pilots(id),
  aircraft_type TEXT NOT NULL,
  mission_name TEXT,
  start_time TIMESTAMP WITH TIME ZONE NOT NULL,
  end_time TIMESTAMP WITH TIME ZONE,
  duration_seconds INTEGER,
  max_altitude_feet INTEGER,
  max_speed_knots INTEGER,
  distance_nm DOUBLE PRECISION,
  kills INTEGER DEFAULT 0,
  deaths INTEGER DEFAULT 0,
  tacview_filename TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE flight_events (
  id BIGSERIAL PRIMARY KEY,
  flight_id BIGINT NOT NULL REFERENCES flights(id),
  event_type TEXT NOT NULL,
  event_time TIMESTAMP WITH TIME ZONE NOT NULL,
  description TEXT,
  target_name TEXT,
  weapon_used TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_flights_pilot_id ON flights(pilot_id);
CREATE INDEX idx_flights_start_time ON flights(start_time);
CREATE INDEX idx_flight_events_flight_id ON flight_events(flight_id);
CREATE INDEX idx_flight_events_event_type ON flight_events(event_type);
