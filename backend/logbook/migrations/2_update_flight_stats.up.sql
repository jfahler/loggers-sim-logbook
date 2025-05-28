-- Add new columns for simplified statistics
ALTER TABLE flights 
  DROP COLUMN IF EXISTS kills,
  DROP COLUMN IF EXISTS max_altitude_feet,
  DROP COLUMN IF EXISTS max_speed_knots,
  DROP COLUMN IF EXISTS distance_nm;

ALTER TABLE flights 
  ADD COLUMN aa_kills INTEGER DEFAULT 0,
  ADD COLUMN ag_kills INTEGER DEFAULT 0,
  ADD COLUMN frat_kills INTEGER DEFAULT 0,
  ADD COLUMN rtb_count INTEGER DEFAULT 0,
  ADD COLUMN ejections INTEGER DEFAULT 0;

-- Drop flight_events table as we're simplifying
DROP TABLE IF EXISTS flight_events;
