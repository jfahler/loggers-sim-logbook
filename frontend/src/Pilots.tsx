import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from './components/ui/card';

export default function Pilots() {
  const [pilotSlugs, setPilotSlugs] = useState<string[]>([]);

  useEffect(() => {
    fetch('/pilot_profiles/index.json')  // served from backend/static dir
      .then((res) => res.json())
      .then(setPilotSlugs)
      .catch(() => setPilotSlugs([]));
  }, []);

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Pilot Roster</h1>
      <div className="grid gap-4">
        {pilotSlugs.map((slug) => (
          <Link key={slug} to={`/pilot/${slug}`}>
            <Card>
              <CardContent className="p-4">
                <h2 className="text-lg font-semibold capitalize">{slug.replace(/_/g, ' ')}</h2>
                <p className="text-sm text-gray-600">View profile →</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
