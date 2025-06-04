// This file was bundled by Encore v1.48.2
//
// https://encore.dev

// encore.gen/internal/entrypoints/combined/main.ts
import { registerGateways, registerHandlers, run } from "encore.dev/internal/codegen/appinit";

// discord/send_pilot_stats.ts
import { api } from "encore.dev/api";
import { secret } from "encore.dev/config";
var discordWebhookUrl = secret("DiscordWebhookUrl");
var sendPilotStats = api(
  { expose: true, method: "POST", path: "/discord/pilot-stats" },
  async (req) => {
    const webhookUrl = discordWebhookUrl();
    if (!webhookUrl) {
      return {
        success: false,
        message: "Discord webhook URL not configured"
      };
    }
    const totalKills = req.totalAaKills + req.totalAgKills;
    const killDeathRatio = req.totalDeaths > 0 ? (totalKills / req.totalDeaths).toFixed(2) : totalKills.toString();
    const embed = {
      title: "📊 Pilot Statistics",
      color: 39423,
      fields: [
        {
          name: "Pilot",
          value: req.pilotCallsign ? `${req.pilotName} (${req.pilotCallsign})` : req.pilotName,
          inline: false
        },
        {
          name: "Total Flights",
          value: req.totalFlights.toString(),
          inline: true
        },
        {
          name: "Total Flight Time",
          value: formatDuration(req.totalFlightTime),
          inline: true
        },
        {
          name: "Average Flight Duration",
          value: formatDuration(req.averageFlightDuration),
          inline: true
        },
        {
          name: "A-A Kills",
          value: req.totalAaKills.toString(),
          inline: true
        },
        {
          name: "A-G Kills",
          value: req.totalAgKills.toString(),
          inline: true
        },
        {
          name: "Total Kills",
          value: totalKills.toString(),
          inline: true
        },
        {
          name: "Friendly Kills",
          value: req.totalFratKills.toString(),
          inline: true
        },
        {
          name: "RTB Count",
          value: req.totalRtbCount.toString(),
          inline: true
        },
        {
          name: "Ejections",
          value: req.totalEjections.toString(),
          inline: true
        },
        {
          name: "Deaths",
          value: req.totalDeaths.toString(),
          inline: true
        },
        {
          name: "K/D Ratio",
          value: killDeathRatio,
          inline: true
        },
        {
          name: "Favorite Aircraft",
          value: req.favoriteAircraft,
          inline: false
        }
      ],
      timestamp: (/* @__PURE__ */ new Date()).toISOString(),
      footer: {
        text: "DCS Pilot Logbook"
      }
    };
    const payload = {
      embeds: [embed]
    };
    try {
      const response = await fetch(webhookUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });
      if (response.ok) {
        return {
          success: true,
          message: "Pilot statistics sent to Discord successfully"
        };
      } else {
        return {
          success: false,
          message: `Failed to send to Discord: ${response.status} ${response.statusText}`
        };
      }
    } catch (error) {
      return {
        success: false,
        message: `Error sending to Discord: ${error}`
      };
    }
  }
);
function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor(seconds % 3600 / 60);
  const remainingSeconds = seconds % 60;
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    return `${remainingSeconds}s`;
  }
}

// discord/webhook.ts
import { api as api2 } from "encore.dev/api";
import { secret as secret2 } from "encore.dev/config";
var discordWebhookUrl2 = secret2("DiscordWebhookUrl");
var sendFlightSummary = api2(
  { expose: true, method: "POST", path: "/discord/flight-summary" },
  async (req) => {
    const webhookUrl = discordWebhookUrl2();
    if (!webhookUrl) {
      return {
        success: false,
        message: "Discord webhook URL not configured"
      };
    }
    const embed = {
      title: "🛩️ Flight Summary",
      color: 65280,
      fields: [
        {
          name: "Pilot",
          value: req.pilotCallsign ? `${req.pilotName} (${req.pilotCallsign})` : req.pilotName,
          inline: true
        },
        {
          name: "Aircraft",
          value: req.aircraftType,
          inline: true
        },
        {
          name: "Mission",
          value: req.missionName || "Unknown",
          inline: true
        },
        {
          name: "Duration",
          value: req.durationSeconds ? formatDuration2(req.durationSeconds) : "Unknown",
          inline: true
        },
        {
          name: "A-A Kills",
          value: req.aaKills.toString(),
          inline: true
        },
        {
          name: "A-G Kills",
          value: req.agKills.toString(),
          inline: true
        },
        {
          name: "Friendly Kills",
          value: req.fratKills.toString(),
          inline: true
        },
        {
          name: "RTB Count",
          value: req.rtbCount.toString(),
          inline: true
        },
        {
          name: "Ejections",
          value: req.ejections.toString(),
          inline: true
        },
        {
          name: "Deaths",
          value: req.deaths.toString(),
          inline: true
        }
      ],
      timestamp: req.startTime.toISOString(),
      footer: {
        text: "DCS Pilot Logbook"
      }
    };
    const payload = {
      embeds: [embed]
    };
    try {
      const response = await fetch(webhookUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });
      if (response.ok) {
        return {
          success: true,
          message: "Flight summary sent to Discord successfully"
        };
      } else {
        return {
          success: false,
          message: `Failed to send to Discord: ${response.status} ${response.statusText}`
        };
      }
    } catch (error) {
      return {
        success: false,
        message: `Error sending to Discord: ${error}`
      };
    }
  }
);
function formatDuration2(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor(seconds % 3600 / 60);
  const remainingSeconds = seconds % 60;
  if (hours > 0) {
    return `${hours}h ${minutes}m ${remainingSeconds}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    return `${remainingSeconds}s`;
  }
}

// logbook/get_flight.ts
import { api as api3, APIError } from "encore.dev/api";

// logbook/db.ts
import { SQLDatabase } from "encore.dev/storage/sqldb";
var logbookDB = new SQLDatabase("logbook", {
  migrations: "./migrations"
});

// logbook/get_flight.ts
var getFlight = api3(
  { expose: true, method: "GET", path: "/flights/:id" },
  async (req) => {
    const flight = await logbookDB.queryRow`
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

// logbook/list_flights.ts
import { api as api4 } from "encore.dev/api";
var listFlights = api4(
  { expose: true, method: "GET", path: "/flights" },
  async (req) => {
    const limit = req.limit || 50;
    const offset = req.offset || 0;
    let flights;
    let total;
    if (req.pilotId) {
      flights = await logbookDB.queryAll`
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
      total = await logbookDB.queryRow`
        SELECT COUNT(*) as count FROM flights f
        WHERE f.pilot_id = ${req.pilotId}
      `;
    } else {
      flights = await logbookDB.queryAll`
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
      total = await logbookDB.queryRow`
        SELECT COUNT(*) as count FROM flights f
      `;
    }
    const flightSummaries = flights.map((flight) => ({
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

// logbook/list_pilots.ts
import { api as api5 } from "encore.dev/api";
var listPilots = api5(
  { expose: true, method: "GET", path: "/pilots" },
  async () => {
    const pilots = await logbookDB.queryAll`
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
    const pilotStats = [];
    for (const pilot of pilots) {
      const favoriteAircraft = await logbookDB.queryRow`
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
        favoriteAircraft: favoriteAircraft?.aircraft_type || "None",
        averageFlightDuration: pilot.average_flight_duration
      });
    }
    return { pilots: pilotStats };
  }
);

// logbook/upload.ts
import { api as api6, APIError as APIError2 } from "encore.dev/api";
import { Bucket } from "encore.dev/storage/objects";
var tacviewBucket = new Bucket("tacview-files");
var uploadTacview = api6(
  { expose: true, method: "POST", path: "/tacview/upload" },
  async (req) => {
    console.log("Upload API called with:", {
      filename: req.filename,
      hasFileData: !!req.fileData,
      fileDataLength: req.fileData?.length || 0
    });
    try {
      if (!req.filename || !req.fileData) {
        console.error("Missing required fields:", { filename: !!req.filename, fileData: !!req.fileData });
        throw APIError2.invalidArgument("filename and fileData are required");
      }
      if (typeof req.filename !== "string" || req.filename.trim().length === 0) {
        console.error("Invalid filename:", req.filename);
        throw APIError2.invalidArgument("filename must be a non-empty string");
      }
      const validExtensions = [".acmi", ".txt"];
      const fileExtension = req.filename.toLowerCase().substring(req.filename.lastIndexOf("."));
      if (!validExtensions.includes(fileExtension)) {
        console.error("Invalid file extension:", fileExtension);
        throw APIError2.invalidArgument("file must have .acmi or .txt extension");
      }
      if (typeof req.fileData !== "string" || req.fileData.trim().length === 0) {
        console.error("Invalid fileData type or empty:", typeof req.fileData, req.fileData?.length);
        throw APIError2.invalidArgument("fileData must be a non-empty string");
      }
      let fileBuffer;
      try {
        console.log("Converting base64 to buffer...");
        fileBuffer = Buffer.from(req.fileData, "base64");
        console.log("Buffer created, size:", fileBuffer.length);
        if (fileBuffer.length > 50 * 1024 * 1024) {
          console.error("File too large:", fileBuffer.length);
          throw APIError2.invalidArgument("file size exceeds 50MB limit");
        }
        if (fileBuffer.length === 0) {
          console.error("Empty file buffer");
          throw APIError2.invalidArgument("file data is empty");
        }
      } catch (error) {
        console.error("Base64 conversion error:", error);
        throw APIError2.invalidArgument("invalid base64 file data");
      }
      let fileContent;
      try {
        console.log("Converting buffer to UTF-8 string...");
        fileContent = fileBuffer.toString("utf-8");
        console.log("File content length:", fileContent.length);
      } catch (error) {
        console.error("UTF-8 conversion error:", error);
        throw APIError2.invalidArgument("file content is not valid UTF-8 text");
      }
      console.log("Parsing Tacview file...");
      const flightData = parseTacviewFile(fileContent, req.filename);
      console.log("Parsed flight data:", {
        pilotName: flightData.pilotName,
        aircraftType: flightData.aircraftType,
        aaKills: flightData.aaKills,
        agKills: flightData.agKills,
        fratKills: flightData.fratKills,
        rtbCount: flightData.rtbCount,
        ejections: flightData.ejections,
        deaths: flightData.deaths
      });
      if (!flightData.pilotName || flightData.pilotName.trim().length === 0) {
        console.error("No pilot name extracted");
        throw APIError2.invalidArgument("could not extract pilot name from file");
      }
      if (!flightData.aircraftType || flightData.aircraftType.trim().length === 0) {
        console.error("No aircraft type extracted");
        throw APIError2.invalidArgument("could not extract aircraft type from file");
      }
      console.log("Creating or finding pilot...");
      let pilot = await logbookDB.queryRow`
        SELECT id FROM pilots WHERE name = ${flightData.pilotName}
      `;
      if (!pilot) {
        console.log("Creating new pilot...");
        pilot = await logbookDB.queryRow`
          INSERT INTO pilots (name, callsign) 
          VALUES (${flightData.pilotName}, ${flightData.callsign || null})
          RETURNING id
        `;
      }
      if (!pilot) {
        console.error("Failed to create or retrieve pilot");
        throw APIError2.internal("failed to create or retrieve pilot");
      }
      console.log("Pilot ID:", pilot.id);
      console.log("Creating flight record...");
      const flight = await logbookDB.queryRow`
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
        console.error("Failed to create flight record");
        throw APIError2.internal("failed to create flight record");
      }
      console.log("Flight ID:", flight.id);
      const response = {
        flightId: flight.id,
        message: `Successfully processed flight for ${flightData.pilotName} in ${flightData.aircraftType}`
      };
      console.log("Upload completed successfully:", response);
      return response;
    } catch (error) {
      if (error instanceof APIError2) {
        console.error("API Error:", error.code, error.message);
        throw error;
      }
      console.error("Unexpected error during upload processing:", error);
      throw APIError2.internal(`failed to process Tacview file: ${error}`);
    }
  }
);
function parseTacviewFile(content, filename) {
  console.log("Starting simplified Tacview file parsing...");
  const lines = content.split("\n");
  console.log("Total lines to parse:", lines.length);
  const flightData = {
    pilotName: "Unknown Pilot",
    aircraftType: "Unknown Aircraft",
    missionName: filename.replace(".acmi", "").replace(".txt", ""),
    startTime: /* @__PURE__ */ new Date(),
    aaKills: 0,
    agKills: 0,
    fratKills: 0,
    rtbCount: 0,
    ejections: 0,
    deaths: 0
  };
  let currentTime = 0;
  let pilotObjectId = null;
  let startTime = null;
  let endTime = null;
  try {
    for (let i = 0; i < lines.length; i++) {
      const trimmedLine = lines[i].trim();
      if (!trimmedLine)
        continue;
      if (trimmedLine.startsWith("0,ReferenceTime=")) {
        const timeStr = trimmedLine.split("=")[1];
        try {
          flightData.startTime = new Date(timeStr);
          console.log("Parsed start time:", flightData.startTime);
        } catch (e) {
          console.warn("Failed to parse reference time:", timeStr);
          flightData.startTime = /* @__PURE__ */ new Date();
        }
        continue;
      }
      if (trimmedLine.startsWith("#")) {
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
      if (trimmedLine.includes(",") && !trimmedLine.startsWith("#")) {
        const parts = trimmedLine.split(",");
        const objectId = parts[0];
        for (const part of parts) {
          if (part.startsWith("Name=")) {
            const name = part.substring(5);
            if (name.includes("|")) {
              const nameParts = name.split("|");
              flightData.pilotName = nameParts[0] || "Unknown Pilot";
              if (nameParts.length > 1 && nameParts[1]) {
                flightData.callsign = nameParts[1];
              }
            } else {
              flightData.pilotName = name || "Unknown Pilot";
            }
            pilotObjectId = objectId;
            console.log("Found pilot:", flightData.pilotName, "callsign:", flightData.callsign);
          }
          if (part.startsWith("Type=")) {
            const type = part.substring(5);
            if (objectId === pilotObjectId && type) {
              flightData.aircraftType = type;
              console.log("Found aircraft type:", flightData.aircraftType);
            }
          }
        }
      }
      if (trimmedLine.includes("Event=")) {
        const eventLine = trimmedLine.toLowerCase();
        if (eventLine.includes("destroyed") && (eventLine.includes("aircraft") || eventLine.includes("plane") || eventLine.includes("fighter") || eventLine.includes("bomber"))) {
          flightData.aaKills++;
          console.log("Found A-A kill event at time:", currentTime);
        } else if (eventLine.includes("destroyed") && (eventLine.includes("tank") || eventLine.includes("vehicle") || eventLine.includes("ground") || eventLine.includes("sam") || eventLine.includes("aaa"))) {
          flightData.agKills++;
          console.log("Found A-G kill event at time:", currentTime);
        } else if (eventLine.includes("friendly") && eventLine.includes("destroyed")) {
          flightData.fratKills++;
          console.log("Found friendly kill event at time:", currentTime);
        } else if (eventLine.includes("rtb") || eventLine.includes("return") || eventLine.includes("landed")) {
          flightData.rtbCount++;
          console.log("Found RTB event at time:", currentTime);
        } else if (eventLine.includes("eject") || eventLine.includes("bailout")) {
          flightData.ejections++;
          console.log("Found ejection event at time:", currentTime);
        } else if (eventLine.includes("pilot killed") || eventLine.includes("crashed") || eventLine.includes("kia")) {
          flightData.deaths++;
          console.log("Found death event at time:", currentTime);
        }
      }
    }
  } catch (error) {
    console.error("Error parsing Tacview file:", error);
  }
  if (startTime !== null && endTime !== null && endTime > startTime) {
    flightData.durationSeconds = Math.round(endTime - startTime);
    flightData.endTime = new Date(flightData.startTime.getTime() + flightData.durationSeconds * 1e3);
  }
  console.log("Parsing completed. Final flight data:", {
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

// discord/encore.service.ts
import { Service } from "encore.dev/service";
var encore_service_default = new Service("discord");

// logbook/encore.service.ts
import { Service as Service2 } from "encore.dev/service";
var encore_service_default2 = new Service2("logbook");

// encore.gen/internal/entrypoints/combined/main.ts
var gateways = [];
var handlers = [
  {
    apiRoute: {
      service: "discord",
      name: "sendPilotStats",
      handler: sendPilotStats,
      raw: false,
      streamingRequest: false,
      streamingResponse: false
    },
    endpointOptions: { "expose": true, "auth": false, "isRaw": false, "isStream": false, "tags": [] },
    middlewares: encore_service_default.cfg.middlewares || []
  },
  {
    apiRoute: {
      service: "discord",
      name: "sendFlightSummary",
      handler: sendFlightSummary,
      raw: false,
      streamingRequest: false,
      streamingResponse: false
    },
    endpointOptions: { "expose": true, "auth": false, "isRaw": false, "isStream": false, "tags": [] },
    middlewares: encore_service_default.cfg.middlewares || []
  },
  {
    apiRoute: {
      service: "logbook",
      name: "getFlight",
      handler: getFlight,
      raw: false,
      streamingRequest: false,
      streamingResponse: false
    },
    endpointOptions: { "expose": true, "auth": false, "isRaw": false, "isStream": false, "tags": [] },
    middlewares: encore_service_default2.cfg.middlewares || []
  },
  {
    apiRoute: {
      service: "logbook",
      name: "listFlights",
      handler: listFlights,
      raw: false,
      streamingRequest: false,
      streamingResponse: false
    },
    endpointOptions: { "expose": true, "auth": false, "isRaw": false, "isStream": false, "tags": [] },
    middlewares: encore_service_default2.cfg.middlewares || []
  },
  {
    apiRoute: {
      service: "logbook",
      name: "listPilots",
      handler: listPilots,
      raw: false,
      streamingRequest: false,
      streamingResponse: false
    },
    endpointOptions: { "expose": true, "auth": false, "isRaw": false, "isStream": false, "tags": [] },
    middlewares: encore_service_default2.cfg.middlewares || []
  },
  {
    apiRoute: {
      service: "logbook",
      name: "uploadTacview",
      handler: uploadTacview,
      raw: false,
      streamingRequest: false,
      streamingResponse: false
    },
    endpointOptions: { "expose": true, "auth": false, "isRaw": false, "isStream": false, "tags": [] },
    middlewares: encore_service_default2.cfg.middlewares || []
  }
];
registerGateways(gateways);
registerHandlers(handlers);
await run(import.meta.url);
//# sourceMappingURL=main.mjs.map
