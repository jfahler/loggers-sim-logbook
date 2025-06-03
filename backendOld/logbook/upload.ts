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
  { expose: true, method: "POST", path: "/tacview/upload" },
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
        aaKills: flightData.aaKills,
        agKills: flightData.agKills,
        fratKills: flightData.fratKills,
        rtbCount: flightData.rtbCount,
        ejections: flightData.ejections,
        deaths: flightData.deaths
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

      // Create flight record with simplified stats
      console.log('Creating flight record...');
      const flight = await logbookDB.queryRow<{ id: number }>`
        INSERT INTO flights (
          pilot_id, aircraft_type, mission_name, start_time, end_time,
          duration_seconds, aa_kills, ag_kills, frat_kills, rtb_count,
          ejections, deaths, tacview_filename
        ) VALUES (
          ${pilot.id}, ${flightData.aircraftType}, ${flightData.missionName || null},
          ${flightData.startTime}, ${flightData.endTime || null}, ${flightData.durationSeconds || null},
          ${flightData.aaKills}, ${flightData.agKills}, ${flightData.fratKills}, ${flightData.rtbCount},
          ${flightData.ejections}, ${flightData.deaths}, ${req.filename}
        )
        RETURNING id
      `;

      if (!flight) {
        console.error('Failed to create flight record');
        throw APIError.internal("failed to create flight record");
      }

      console.log('Flight ID:', flight.id);

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
  aaKills: number; // Air-to-Air kills
  agKills: number; // Air-to-Ground kills
  fratKills: number; // Friendly kills
  rtbCount: number; // Return to base count
  ejections: number; // Number of ejections
  deaths: number; // Deaths/KIA
}

function parseTacviewFile(content: string, filename: string): ParsedFlightData {
  console.log('Starting simplified Tacview file parsing...');
  const lines = content.split('\n');
  console.log('Total lines to parse:', lines.length);
  
  // Initialize default values
  const flightData: ParsedFlightData = {
    pilotName: 'Unknown Pilot',
    aircraftType: 'Unknown Aircraft',
    missionName: filename.replace('.acmi', '').replace('.txt', ''),
    startTime: new Date(),
    aaKills: 0,
    agKills: 0,
    fratKills: 0,
    rtbCount: 0,
    ejections: 0,
    deaths: 0
  };

  let currentTime = 0;
  let pilotObjectId: string | null = null;
  let startTime: number | null = null;
  let endTime: number | null = null;

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
          if (startTime === null) {
            startTime = parsedTime;
          }
          endTime = parsedTime;
        }
        continue;
      }

      // Parse object data to identify pilot and aircraft
      if (trimmedLine.includes(',') && !trimmedLine.startsWith('#')) {
        const parts = trimmedLine.split(',');
        const objectId = parts[0];
        
        for (const part of parts) {
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

      // Parse events for simplified statistics
      if (trimmedLine.includes('Event=')) {
        const eventLine = trimmedLine.toLowerCase();
        
        // Air-to-Air kills (aircraft destroyed)
        if (eventLine.includes('destroyed') && (eventLine.includes('aircraft') || eventLine.includes('plane') || eventLine.includes('fighter') || eventLine.includes('bomber'))) {
          flightData.aaKills++;
          console.log('Found A-A kill event at time:', currentTime);
        }
        
        // Air-to-Ground kills (ground targets destroyed)
        else if (eventLine.includes('destroyed') && (eventLine.includes('tank') || eventLine.includes('vehicle') || eventLine.includes('ground') || eventLine.includes('sam') || eventLine.includes('aaa'))) {
          flightData.agKills++;
          console.log('Found A-G kill event at time:', currentTime);
        }
        
        // Friendly kills
        else if (eventLine.includes('friendly') && eventLine.includes('destroyed')) {
          flightData.fratKills++;
          console.log('Found friendly kill event at time:', currentTime);
        }
        
        // Return to base
        else if (eventLine.includes('rtb') || eventLine.includes('return') || eventLine.includes('landed')) {
          flightData.rtbCount++;
          console.log('Found RTB event at time:', currentTime);
        }
        
        // Ejections
        else if (eventLine.includes('eject') || eventLine.includes('bailout')) {
          flightData.ejections++;
          console.log('Found ejection event at time:', currentTime);
        }
        
        // Deaths/KIA
        else if (eventLine.includes('pilot killed') || eventLine.includes('crashed') || eventLine.includes('kia')) {
          flightData.deaths++;
          console.log('Found death event at time:', currentTime);
        }
      }
    }
  } catch (error) {
    console.error('Error parsing Tacview file:', error);
    // Continue with default values
  }

  // Calculate duration if we have time data
  if (startTime !== null && endTime !== null && endTime > startTime) {
    flightData.durationSeconds = Math.round(endTime - startTime);
    flightData.endTime = new Date(flightData.startTime.getTime() + flightData.durationSeconds * 1000);
  }

  console.log('Parsing completed. Final flight data:', {
    pilotName: flightData.pilotName,
    aircraftType: flightData.aircraftType,
    duration: flightData.durationSeconds,
    aaKills: flightData.aaKills,
    agKills: flightData.agKills,
    fratKills: flightData.fratKills,
    rtbCount: flightData.rtbCount,
    ejections: flightData.ejections,
    deaths: flightData.deaths
  });

  return flightData;
}
