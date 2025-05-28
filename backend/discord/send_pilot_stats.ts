import { api } from "encore.dev/api";
import { secret } from "encore.dev/config";

const discordWebhookUrl = secret("DiscordWebhookUrl");

export interface SendPilotStatsRequest {
  pilotName: string;
  pilotCallsign?: string | null;
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

export interface SendPilotStatsResponse {
  success: boolean;
  message: string;
}

// Sends pilot statistics to Discord via webhook.
export const sendPilotStats = api<SendPilotStatsRequest, SendPilotStatsResponse>(
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
      color: 0x0099ff,
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
      timestamp: new Date().toISOString(),
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

function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    return `${remainingSeconds}s`;
  }
}
