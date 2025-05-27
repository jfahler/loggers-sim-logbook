import { api, APIError } from "encore.dev/api";
import { Bucket } from "encore.dev/storage/objects";
import { logbookDB } from "./db";

const tacviewBucket = new Bucket("tacview-files");

export interface UploadTacviewRequest {
  filename: string;
  fileData: string; // base64 encoded file data
}

export interface UploadTacviewResponse {
  flightId: number;
  message: string;
}

// Uploads a Tacview file and processes it to extract flight data.
export const uploadTacview = api<UploadTacviewRequest, UploadTacviewResponse>(
  { expose: true, method: "POST", path: "/logbook/tacview/upload" },
  async (req) => {
    console.log('Upload API called with:', {
      filename: req.filename,
      hasFileData: !!req.fileData,
      fileDataLength: req.fileData?.length || 0
    });

    try {
      // Validate input
      if (!req.filename || !req.fileData) {
        console.error('Missing required fields:', { filename: !!req.filename, fileData: !!req.fileData });
        throw APIError.invalidArgument("filename and fileData are required");
      }

      // Validate filename
      if (typeof req.filename !== 'string' || req.filename.trim().length === 0) {
        console.error('Invalid filename:', req.filename);
        throw APIError.invalidArgument("filename must be a non-empty string");
      }

      // Validate file extension
      const validExtensions = ['.acmi', '.txt'];
      const fileExtension = req.filename.toLowerCase().substring(req.filename.lastIndexOf('.'));
      if (!validExtensions.includes(fileExtension)) {
        console.error('Invalid file extension:', fileExtension);
        throw APIError.invalidArgument("file must have .acmi or .txt extension");
      }

      // Validate base64 data
      if (typeof req.fileData !== 'string' || req.fileData.trim().length === 0) {
        console.error('Invalid fileData type or empty:', typeof req.fileData, req.fileData?.length);
        throw APIError.invalidArgument("fileData must be a non-empty string");
      }

      let fileBuffer: Buffer;
      try {
        console.log('Converting base64 to buffer...');
        fileBuffer = Buffer.from(req.fileData, 'base64');
        console.log('Buffer created, size:', fileBuffer.length);
        
        // Validate buffer size (max 50MB)
        if (fileBuffer.length > 50 * 1024 * 1024) {
          console.error('File too large:', fileBuffer.length);
          throw APIError.invalidArgument("file size exceeds 50MB limit");
        }
        
        // Validate buffer is not empty
        if (fileBuffer.length === 0) {
          console.error('Empty file buffer');
          throw APIError.invalidArgument("file data is empty");
        }
      } catch (error) {
        console.error('Base64 conversion error:', error);
        throw APIError.invalidArgument("invalid base64 file data");
      }

      // Store the file in object storage
      try {
        console.log('Uploading to object storage...');
        await tacviewBucket.upload(req.filename, fileBuffer, {
          contentType: 'application/octet-stream'
        });
        console.log('File uploaded to object storage successfully');
      } catch (error) {
        console.error('Object storage error:', error);
        throw APIError.internal(`failed to store file: ${error}`);
      }

      // Parse the Tacview file content
      let fileContent: string;
      try {
        console.log('Converting buffer to UTF-8 string...');
        fileContent = fileBuffer.toString('utf-8');
        console.log('File content length:', fileContent.length);
      } catch (error) {
        console.error('UTF-8 conversion error:', error);
        throw APIError.invalidArgument("file content is not valid UTF-8 text");
      }

      console.log('Parsing Tacview file...');
      const flightData = parseTacviewFile(fileContent, req.filename);
      console.log('Parsed flight data:', {
        pilotName: flightData.pilotName,
        aircraftType: flightData.aircraftType,
        kills: flightData.kills,
        deaths: flightData.deaths,
        eventsCount: flightData.events.length
      });

      // Validate parsed flight data
      if (!flightData.pilotName || flightData.pilotName.trim().length === 0) {
        console.error('No pilot name extracted');
        throw APIError.invalidArgument("could not extract pilot name from file");
      }

      if (!flightData.aircraftType || flightData.aircraftType.trim().length === 0) {
        console.error('No aircraft type extracted');
        throw APIError.invalidArgument("could not extract aircraft type from file");
      }

      // Create or get pilot
      console.log('Creating or finding pilot...');
      let pilot = await logbookDB.queryRow<{ id: number }>`
        SELECT id FROM pilots WHERE name = ${flightData.pilotName}
      `;

      if (!pilot) {
        console.log('Creating new pilot...');
        pilot = await logbookDB.queryRow<{ id: number }>`
          INSERT INTO pilots (name, callsign) 
          VALUES (${flightData.pilotName}, ${flightData.callsign || null})
          RETURNING id
        `;
      }

      if (!pilot) {
        console.error('Failed to create or retrieve pilot');
        throw APIError.internal("failed to create or retrieve pilot");
      }

      console.log('Pilot ID:', pilot.id);

      // Create flight record
      console.log('Creating flight record...');
      const flight = await logbookDB.queryRow<{ id: number }>`
        INSERT INTO flights (
          pilot_id, aircraft_type, mission_name, start_time, end_time,
          duration_seconds, max_altitude_feet, max_speed_knots, distance_nm,
          kills, deaths, tacview_filename
        ) VALUES (
          ${pilot.id}, ${flightData.aircraftType}, ${flightData.missionName || null},
          ${flightData.startTime}, ${flightData.endTime || null}, ${flightData.durationSeconds || null},
          ${flightData.maxAltitudeFeet || null}, ${flightData.maxSpeedKnots || null}, ${flightData.distanceNm || null},
          ${flightData.kills}, ${flightData.deaths}, ${req.filename}
        )
        RETURNING id
      `;

      if (!flight) {
        console.error('Failed to create flight record');
        throw APIError.internal("failed to create flight record");
      }

      console.log('Flight ID:', flight.id);

      // Create flight events
      console.log('Creating flight events...');
      for (const event of flightData.events) {
        try {
          await logbookDB.exec`
            INSERT INTO flight_events (
              flight_id, event_type, event_time, description, target_name, weapon_used
            ) VALUES (
              ${flight.id}, ${event.eventType}, ${event.eventTime}, 
              ${event.description || null}, ${event.targetName || null}, ${event.weaponUsed || null}
            )
          `;
        } catch (error) {
          console.error('Error inserting flight event:', error);
          // Continue processing other events
        }
      }

      const response = {
        flightId: flight.id,
        message: `Successfully processed flight for ${flightData.pilotName} in ${flightData.aircraftType}`
      };

      console.log('Upload completed successfully:', response);
      return response;
    } catch (error) {
      if (error instanceof APIError) {
        console.error('API Error:', error.code, error.message);
        throw error;
      }
      console.error('Unexpected error during upload processing:', error);
      throw APIError.internal(`failed to process Tacview file: ${error}`);
    }
  }
);

interface ParsedFlightData {
  pilotName: string;
  callsign?: string;
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
  events: Array<{
    eventType: string;
    eventTime: Date;
    description?: string;
    targetName?: string;
    weaponUsed?: string;
  }>;
}

function parseTacviewFile(content: string, filename: string): ParsedFlightData {
  console.log('Starting Tacview file parsing...');
  const lines = content.split('\n');
  console.log('Total lines to parse:', lines.length);
  
  // Initialize default values
  const flightData: ParsedFlightData = {
    pilotName: 'Unknown Pilot',
    aircraftType: 'Unknown Aircraft',
    missionName: filename.replace('.acmi', '').replace('.txt', ''),
    startTime: new Date(),
    kills: 0,
    deaths: 0,
    events: []
  };

  let currentTime = 0;
  let pilotObjectId: string | null = null;
  let maxAltitude = 0;
  let maxSpeed = 0;
  let totalDistance = 0;
  let lastPosition: { lat: number; lon: number } | null = null;

  try {
    for (let i = 0; i < lines.length; i++) {
      const trimmedLine = lines[i].trim();
      
      // Skip empty lines
      if (!trimmedLine) continue;
      
      // Parse time reference
      if (trimmedLine.startsWith('0,ReferenceTime=')) {
        const timeStr = trimmedLine.split('=')[1];
        try {
          flightData.startTime = new Date(timeStr);
          console.log('Parsed start time:', flightData.startTime);
        } catch (e) {
          console.warn('Failed to parse reference time:', timeStr);
          flightData.startTime = new Date();
        }
        continue;
      }

      // Parse time updates
      if (trimmedLine.startsWith('#')) {
        const timeValue = trimmedLine.substring(1);
        const parsedTime = parseFloat(timeValue);
        if (!isNaN(parsedTime)) {
          currentTime = parsedTime;
        }
        continue;
      }

      // Parse object data
      if (trimmedLine.includes(',T=')) {
        const parts = trimmedLine.split(',');
        const objectId = parts[0];
        
        for (const part of parts) {
          if (part.startsWith('T=')) {
            const coords = part.substring(2).split('|');
            if (coords.length >= 3) {
              const lon = parseFloat(coords[0]);
              const lat = parseFloat(coords[1]);
              const altMeters = parseFloat(coords[2]);
              
              if (!isNaN(lon) && !isNaN(lat) && !isNaN(altMeters)) {
                const alt = altMeters * 3.28084; // Convert meters to feet
                
                if (alt > maxAltitude) {
                  maxAltitude = alt;
                }

                // Calculate distance if we have a previous position
                if (lastPosition && objectId === pilotObjectId) {
                  const distance = calculateDistance(lastPosition.lat, lastPosition.lon, lat, lon);
                  if (!isNaN(distance)) {
                    totalDistance += distance;
                  }
                }
                
                if (objectId === pilotObjectId) {
                  lastPosition = { lat, lon };
                }
              }
            }
          }
          
          if (part.startsWith('Name=')) {
            const name = part.substring(5);
            if (name.includes('|')) {
              const nameParts = name.split('|');
              flightData.pilotName = nameParts[0] || 'Unknown Pilot';
              if (nameParts.length > 1 && nameParts[1]) {
                flightData.callsign = nameParts[1];
              }
            } else {
              flightData.pilotName = name || 'Unknown Pilot';
            }
            pilotObjectId = objectId;
            console.log('Found pilot:', flightData.pilotName, 'callsign:', flightData.callsign);
          }
          
          if (part.startsWith('Type=')) {
            const type = part.substring(5);
            if (objectId === pilotObjectId && type) {
              flightData.aircraftType = type;
              console.log('Found aircraft type:', flightData.aircraftType);
            }
          }
        }
      }

      // Parse events (kills, deaths, etc.)
      if (trimmedLine.includes('Event=')) {
        const eventTime = new Date(flightData.startTime.getTime() + currentTime * 1000);
        
        if (trimmedLine.includes('Destroyed')) {
          flightData.events.push({
            eventType: 'KILL',
            eventTime,
            description: 'Target destroyed'
          });
          flightData.kills++;
          console.log('Found kill event at time:', currentTime);
        }
        
        if (trimmedLine.includes('Pilot killed') || trimmedLine.includes('Crashed')) {
          flightData.events.push({
            eventType: 'DEATH',
            eventTime,
            description: 'Pilot killed or crashed'
          });
          flightData.deaths++;
          console.log('Found death event at time:', currentTime);
        }
      }
    }
  } catch (error) {
    console.error('Error parsing Tacview file:', error);
    // Continue with default values
  }

  // Set calculated values
  flightData.maxAltitudeFeet = Math.round(maxAltitude);
  flightData.maxSpeedKnots = Math.round(maxSpeed);
  flightData.distanceNm = totalDistance;
  
  if (currentTime > 0) {
    flightData.endTime = new Date(flightData.startTime.getTime() + currentTime * 1000);
    flightData.durationSeconds = Math.round(currentTime);
  }

  console.log('Parsing completed. Final flight data:', {
    pilotName: flightData.pilotName,
    aircraftType: flightData.aircraftType,
    duration: flightData.durationSeconds,
    kills: flightData.kills,
    deaths: flightData.deaths,
    events: flightData.events.length,
    maxAltitude: flightData.maxAltitudeFeet
  });

  return flightData;
}

function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  try {
    const R = 3440.065; // Earth's radius in nautical miles
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  } catch (error) {
    return 0;
  }
}
