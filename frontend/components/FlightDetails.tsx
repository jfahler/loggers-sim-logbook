import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, Plane, Clock, Target, Skull, Send, MapPin, Gauge } from 'lucide-react';
import backend from '~backend/client';

interface FlightDetailsProps {
  flightId: number;
  onBack: () => void;
}

export function FlightDetails({ flightId, onBack }: FlightDetailsProps) {
  const { toast } = useToast();

  const { data: flight, isLoading } = useQuery({
    queryKey: ['flight', flightId],
    queryFn: () => backend.logbook.getFlight({ id: flightId }),
  });

  const sendToDiscordMutation = useMutation({
    mutationFn: () => {
      if (!flight) throw new Error('No flight data');
      return backend.discord.sendFlightSummary({
        flightId: flight.id,
        pilotName: flight.pilotName,
        pilotCallsign: flight.pilotCallsign || null,
        aircraftType: flight.aircraftType,
        missionName: flight.missionName || null,
        startTime: flight.startTime,
        durationSeconds: flight.durationSeconds || null,
        kills: flight.kills,
        deaths: flight.deaths,
        maxAltitudeFeet: flight.maxAltitudeFeet || null,
        maxSpeedKnots: flight.maxSpeedKnots || null,
        distanceNm: flight.distanceNm || null,
      });
    },
    onSuccess: (data) => {
      if (data.success) {
        toast({
          title: "Success",
          description: data.message,
        });
      } else {
        toast({
          title: "Error",
          description: data.message,
          variant: "destructive",
        });
      }
    },
    onError: (error) => {
      console.error('Error sending to Discord:', error);
      toast({
        title: "Error",
        description: "Failed to send flight summary to Discord",
        variant: "destructive",
      });
    },
  });

  const formatDuration = (seconds: number) => {
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
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading flight details...</div>;
  }

  if (!flight) {
    return <div className="text-center py-8">Flight not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" onClick={onBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Flights
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Flight Details</h1>
            <p className="text-gray-600">
              {flight.pilotCallsign ? `${flight.pilotName} (${flight.pilotCallsign})` : flight.pilotName}
            </p>
          </div>
        </div>
        <Button
          onClick={() => sendToDiscordMutation.mutate()}
          disabled={sendToDiscordMutation.isPending}
        >
          <Send className="h-4 w-4 mr-2" />
          Send to Discord
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Flight Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Aircraft</p>
                  <p className="font-medium">{flight.aircraftType}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Mission</p>
                  <p className="font-medium">{flight.missionName || 'Unknown'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Start Time</p>
                  <p className="font-medium">
                    {new Date(flight.startTime).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Duration</p>
                  <p className="font-medium">
                    {flight.durationSeconds ? formatDuration(flight.durationSeconds) : 'Unknown'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Flight Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="flex items-center space-x-2">
                  <Target className="h-4 w-4 text-green-600" />
                  <div>
                    <p className="text-sm text-gray-600">Kills</p>
                    <p className="font-semibold text-lg">{flight.kills}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Skull className="h-4 w-4 text-red-600" />
                  <div>
                    <p className="text-sm text-gray-600">Deaths</p>
                    <p className="font-semibold text-lg">{flight.deaths}</p>
                  </div>
                </div>
                {flight.maxAltitudeFeet && (
                  <div className="flex items-center space-x-2">
                    <MapPin className="h-4 w-4 text-blue-600" />
                    <div>
                      <p className="text-sm text-gray-600">Max Altitude</p>
                      <p className="font-semibold text-lg">{flight.maxAltitudeFeet.toLocaleString()} ft</p>
                    </div>
                  </div>
                )}
                {flight.maxSpeedKnots && (
                  <div className="flex items-center space-x-2">
                    <Gauge className="h-4 w-4 text-purple-600" />
                    <div>
                      <p className="text-sm text-gray-600">Max Speed</p>
                      <p className="font-semibold text-lg">{flight.maxSpeedKnots} kts</p>
                    </div>
                  </div>
                )}
              </div>
              {flight.distanceNm && (
                <div className="mt-4 pt-4 border-t">
                  <div className="flex items-center space-x-2">
                    <Plane className="h-4 w-4 text-gray-600" />
                    <div>
                      <p className="text-sm text-gray-600">Distance Traveled</p>
                      <p className="font-semibold">{flight.distanceNm.toFixed(1)} nautical miles</p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div>
          <Card>
            <CardHeader>
              <CardTitle>Flight Events</CardTitle>
            </CardHeader>
            <CardContent>
              {flight.events.length > 0 ? (
                <div className="space-y-3">
                  {flight.events.map((event) => (
                    <div key={event.id} className="flex items-center justify-between">
                      <div>
                        <Badge
                          variant={event.eventType === 'KILL' ? 'default' : 'destructive'}
                        >
                          {event.eventType}
                        </Badge>
                        {event.description && (
                          <p className="text-sm text-gray-600 mt-1">{event.description}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-600">
                          {new Date(event.eventTime).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600 text-center py-4">No events recorded</p>
              )}
            </CardContent>
          </Card>

          {flight.tacviewFilename && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>File Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div>
                  <p className="text-sm text-gray-600">Tacview File</p>
                  <p className="font-medium">{flight.tacviewFilename}</p>
                </div>
                <div className="mt-2">
                  <p className="text-sm text-gray-600">Uploaded</p>
                  <p className="font-medium">
                    {new Date(flight.createdAt).toLocaleString()}
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
