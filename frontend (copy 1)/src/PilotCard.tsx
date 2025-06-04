
import React from "react";

interface PilotProfile {
  callsign: string;
  platform_hours: Record<string, string>;
  aircraft_hours: Record<string, string>;
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
  const { callsign, platform_hours, aircraft_hours, mission_summary } = profile;

  return (
    <div className="bg-white rounded-2xl shadow-md p-4 w-full max-w-md border border-gray-200">
      <h2 className="text-xl font-bold mb-2">{callsign}</h2>

      <div className="mb-2">
        <h3 className="font-semibold text-sm text-gray-600">Total Hours</h3>
        <p className="text-sm">{platform_hours.Total}</p>
      </div>

      <div className="mb-2">
        <h3 className="font-semibold text-sm text-gray-600">Aircraft Flown</h3>
        <ul className="text-sm list-disc list-inside">
          {Object.entries(aircraft_hours).map(([aircraft, time]) => (
            <li key={aircraft}>{aircraft}: {time}</li>
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
