import { api } from "encore.dev/api";
import { secret } from "encore.dev/config";

const discordWebhookUrl = secret("DiscordWebhookUrl");

export interface SendFlightSummaryRequest {
  flightId: number;
  pilotName: string;
  pilotCallsign?: string | null;
  aircraftType: string;
  missionName?: string | null;
  startTime: Date;
  durationSeconds?: number | null;
  aaKills: number;
  agKills: number;
  fratKills: number;
  rtbCount: number;
  ejections: number;
  deaths: number;
}

export interface SendFlightSummaryResponse {
  success: boolean;
  message: string;
}

// Sends a flight summary to Discord via webhook.
export const sendFlightSummary = api<SendFlightSummaryRequest, SendFlightSummaryResponse>(
  { expose: true, method: "POST", path: "/discord/flight-summary" },
  async (req) => {
    const webhookUrl = discordWebhookUrl();
    
    if (!webhookUrl) {
      return {
        success: false,
        message: "Discord webhook URL not configured"
      };
    }

    const embed = {
      title: "🛩️ Flight Summary",
      color: 0x00ff00,
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
          value: req.durationSeconds ? formatDuration(req.durationSeconds) : "Unknown",
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
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
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

function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m ${remainingSeconds}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    return `${remainingSeconds}s`;
  }
}
