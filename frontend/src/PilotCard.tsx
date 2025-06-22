import React, { useState } from "react";

function formatMinutesToHHMM(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return `${h}:${m.toString().padStart(2, '0')}`;
}

interface PilotProfile {
  callsign: string;
  profile_image?: string;
  platform_hours: Record<string, number>;
  aircraft_hours: Record<string, number>;
  mission_summary: {
    logs_flown: number;
    aa_kills: number;
    ag_kills: number;
    frat_kills: number;
    rtb: number;
    kia: number;
  };
}

interface PilotCardProps {
  profile: PilotProfile;
}

export const PilotCard: React.FC<PilotCardProps> = ({ profile }) => {
  const { callsign, profile_image, platform_hours, aircraft_hours, mission_summary } = profile;
  const [hovered, setHovered] = useState(false);

  // Use the provided image or fallback to the default
  // Adjust the path as needed for your frontend-backend setup
  const imageUrl = profile_image && profile_image !== "" ? `/api/pilot_profiles/images/${profile_image}` : `/api/pilot_profiles/images/default.png`;

  return (
    <div className="bg-white rounded-2xl shadow-md p-4 w-full max-w-md border border-gray-200">
      <div className="flex flex-col items-center mb-2">
        <img
          src={imageUrl}
          alt={callsign + " profile"}
          style={{
            maxHeight: hovered ? undefined : 128,
            maxWidth: hovered ? undefined : 128,
            height: hovered ? 'auto' : 128,
            width: hovered ? 'auto' : 128,
            objectFit: 'contain',
            transition: 'all 0.2s',
            cursor: 'pointer',
            borderRadius: 12,
            boxShadow: hovered ? '0 0 16px #888' : undefined,
            zIndex: hovered ? 10 : undefined,
          }}
          onMouseEnter={() => setHovered(true)}
          onMouseLeave={() => setHovered(false)}
        />
      </div>
      <h2 className="text-xl font-bold mb-2 text-center">{callsign}</h2>

      <div className="mb-2">
        <h3 className="font-semibold text-sm text-gray-600">Total Hours</h3>
        <p className="text-sm">{formatMinutesToHHMM(platform_hours.Total)}</p>
      </div>

      <div className="mb-2">
        <h3 className="font-semibold text-sm text-gray-600">Aircraft Flown</h3>
        <ul className="text-sm list-disc list-inside">
          {Object.entries(aircraft_hours).map(([aircraft, time]) => (
            <li key={aircraft}>{aircraft}: {formatMinutesToHHMM(time)}</li>
          ))}
        </ul>
      </div>

      <div className="mb-2">
        <h3 className="font-semibold text-sm text-gray-600">Stats</h3>
        <ul className="text-sm">
          <li>Logs Flown: {mission_summary.logs_flown}</li>
          <li>A-A Kills: {mission_summary.aa_kills}</li>
          <li>A-G Kills: {mission_summary.ag_kills}</li>
          <li>FRAT Kills: {mission_summary.frat_kills}</li>
          <li>RTBs: {mission_summary.rtb}</li>
          <li>KIA: {mission_summary.kia}</li>
        </ul>
      </div>
    </div>
  );
};
