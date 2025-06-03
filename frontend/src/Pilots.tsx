
import React, { useEffect, useState } from "react";
import { PilotCard } from "./PilotCard";

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

export const Pilots: React.FC = () => {
  const [profiles, setProfiles] = useState<PilotProfile[]>([]);

  useEffect(() => {
    const loadProfiles = async () => {
      const files = ["drunkbonsai.json"];
      const loaded: PilotProfile[] = await Promise.all(
        files.map(async (filename) => {
          const res = await fetch(`/pilot_profiles/${filename}`);
          return await res.json();
        })
      );
      setProfiles(loaded);
    };

    loadProfiles();
  }, []);

  return (
    <div className="p-4 flex flex-wrap gap-4 justify-center">
      {profiles.map((profile) => (
        <PilotCard key={profile.callsign} profile={profile} />
      ))}
    </div>
  );
};
