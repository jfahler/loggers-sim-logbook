import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FlightDetails } from '../components/FlightDetails';
import { Plane, Clock, Target, Skull, ChevronLeft, ChevronRight } from 'lucide-react';
import backend from '~backend/client';

export function Flights() {
  const [selectedFlightId, setSelectedFlightId] = useState<number | null>(null);
  const [page, setPage] = useState(0);
  const limit = 20;

  const { data: flights, isLoading } = useQuery({
    queryKey: ['flights', { limit, offset: page * limit }],
    queryFn: () => backend.logbook.listFlights({ limit, offset: page * limit }),
  });

  const totalPages = Math.ceil((flights?.total || 0) / limit);

  if (selectedFlightId) {
    return (
      <FlightDetails
        flightId={selectedFlightId}
        onBack={() => setSelectedFlightId(null)}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Flights</h1>
          <p className="text-gray-600 mt-2">Browse all recorded flights</p>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-8">Loading flights...</div>
      ) : (
        <>
          <div className="grid gap-4">
            {flights?.flights.map((flight) => (
              <Card
                key={flight.id}
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelectedFlightId(flight.id)}
              >
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">
                        {flight.pilotCallsign ? `${flight.pilotName} (${flight.pilotCallsign})` : flight.pilotName}
                      </CardTitle>
                      <p className="text-gray-600">{flight.aircraftType}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600">
                        {new Date(flight.startTime).toLocaleDateString()}
                      </p>
                      <p className="text-sm text-gray-600">
                        {new Date(flight.startTime).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-6">
                      <div className="flex items-center space-x-2">
                        <Clock className="h-4 w-4 text-gray-500" />
                        <span className="text-sm">
                          {flight.durationSeconds ? Math.round(flight.durationSeconds / 60) : 0}m
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Target className="h-4 w-4 text-green-600" />
                        <span className="text-sm">{flight.kills}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Skull className="h-4 w-4 text-red-600" />
                        <span className="text-sm">{flight.deaths}</span>
                      </div>
                      {flight.maxAltitudeFeet && (
                        <div className="flex items-center space-x-2">
                          <Plane className="h-4 w-4 text-blue-600" />
                          <span className="text-sm">{flight.maxAltitudeFeet.toLocaleString()} ft</span>
                        </div>
                      )}
                    </div>
                    <div className="flex space-x-2">
                      {flight.events.map((event, index) => (
                        <Badge
                          key={index}
                          variant={event.eventType === 'KILL' ? 'default' : 'destructive'}
                        >
                          {event.eventType}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  {flight.missionName && (
                    <p className="text-sm text-gray-600 mt-2">Mission: {flight.missionName}</p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex justify-center items-center space-x-4">
              <Button
                variant="outline"
                onClick={() => setPage(page - 1)}
                disabled={page === 0}
              >
                <ChevronLeft className="h-4 w-4 mr-2" />
                Previous
              </Button>
              <span className="text-sm text-gray-600">
                Page {page + 1} of {totalPages}
              </span>
              <Button
                variant="outline"
                onClick={() => setPage(page + 1)}
                disabled={page >= totalPages - 1}
              >
                Next
                <ChevronRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
