import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Plane, Users, Target, Skull } from 'lucide-react';
import backend from '~backend/client';

export function Dashboard() {
  const { data: pilots } = useQuery({
    queryKey: ['pilots'],
    queryFn: () => backend.logbook.listPilots(),
  });

  const { data: flights } = useQuery({
    queryKey: ['flights', { limit: 10 }],
    queryFn: () => backend.logbook.listFlights({ limit: 10 }),
  });

  const totalFlights = flights?.total || 0;
  const totalPilots = pilots?.pilots.length || 0;
  const totalKills = pilots?.pilots.reduce((sum, pilot) => sum + pilot.totalKills, 0) || 0;
  const totalDeaths = pilots?.pilots.reduce((sum, pilot) => sum + pilot.totalDeaths, 0) || 0;

  const stats = [
    {
      title: 'Total Flights',
      value: totalFlights,
      icon: Plane,
      color: 'text-blue-600',
    },
    {
      title: 'Active Pilots',
      value: totalPilots,
      icon: Users,
      color: 'text-green-600',
    },
    {
      title: 'Total Kills',
      value: totalKills,
      icon: Target,
      color: 'text-red-600',
    },
    {
      title: 'Total Deaths',
      value: totalDeaths,
      icon: Skull,
      color: 'text-gray-600',
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Overview of your DCS pilot logbook statistics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  {stat.title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value.toLocaleString()}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Top Pilots by Flights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {pilots?.pilots.slice(0, 5).map((pilot) => (
                <div key={pilot.pilot.id} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">
                      {pilot.pilot.callsign ? `${pilot.pilot.name} (${pilot.pilot.callsign})` : pilot.pilot.name}
                    </p>
                    <p className="text-sm text-gray-600">{pilot.favoriteAircraft}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{pilot.totalFlights} flights</p>
                    <p className="text-sm text-gray-600">{pilot.totalKills} kills</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Flights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {flights?.flights.slice(0, 5).map((flight) => (
                <div key={flight.id} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">
                      {flight.pilotCallsign ? `${flight.pilotName} (${flight.pilotCallsign})` : flight.pilotName}
                    </p>
                    <p className="text-sm text-gray-600">{flight.aircraftType}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">
                      {flight.durationSeconds ? Math.round(flight.durationSeconds / 60) : 0}m
                    </p>
                    <p className="text-sm text-gray-600">
                      {new Date(flight.startTime).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
