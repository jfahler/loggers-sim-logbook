import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, Plane, Clock, Target, Skull, Send, Users, AlertTriangle } from 'lucide-react';
import api from '@/api';

interface FlightDetailsProps {
  flightId: number;
  onBack: () => void;
}

export function FlightDetails({ flightId, onBack }: FlightDetailsProps) {
  const { toast } = useToast();

  const { data: flight, isLoading } = useQuery({
    queryKey: ['flight', flightId],
    queryFn: () => api.getFlight(flightId),
  });

  const sendToDiscordMutation = useMutation({
    mutationFn: () => {
      if (!flight) throw new Error('No flight data');
      return api.sendFlightSummary({
        flightId: flight.id,
        pilotName: flight.pilotName,
        pilotCallsign: flight.pilotCallsign || null,
        aircraftType: flight.aircraftType,
        missionName: flight.missionName || null,
        startTime: flight.startTime,
        durationSeconds: flight.durationSeconds || null,
        aaKills: flight.aaKills,
        agKills: flight.agKills,
        fratKills: flight.fratKills,
        rtbCount: flight.rtbCount,
        ejections: flight.ejections,
        deaths: flight.deaths,
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
              <CardTitle>Combat Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="flex items-center space-x-2">
                  <Target className="h-4 w-4 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-600">A-A Kills</p>
                    <p className="font-semibold text-lg">{flight.aaKills}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Target className="h-4 w-4 text-green-600" />
                  <div>
                    <p className="text-sm text-gray-600">A-G Kills</p>
                    <p className="font-semibold text-lg">{flight.agKills}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4 text-orange-600" />
                  <div>
                    <p className="text-sm text-gray-600">Friendly Kills</p>
                    <p className="font-semibold text-lg">{flight.fratKills}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Plane className="h-4 w-4 text-purple-600" />
                  <div>
                    <p className="text-sm text-gray-600">RTB Count</p>
                    <p className="font-semibold text-lg">{flight.rtbCount}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-yellow-600" />
                  <div>
                    <p className="text-sm text-gray-600">Ejections</p>
                    <p className="font-semibold text-lg">{flight.ejections}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Skull className="h-4 w-4 text-red-600" />
                  <div>
                    <p className="text-sm text-gray-600">Deaths</p>
                    <p className="font-semibold text-lg">{flight.deaths}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div>
          <Card>
            <CardHeader>
              <CardTitle>Performance Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Total Kills</span>
                <Badge variant="default">
                  {flight.aaKills + flight.agKills}
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Kill/Death Ratio</span>
                <Badge variant="outline">
                  {flight.deaths > 0 
                    ? ((flight.aaKills + flight.agKills) / flight.deaths).toFixed(2)
                    : (flight.aaKills + flight.agKills).toString()
                  }
                </Badge>
              </div>
              {flight.fratKills > 0 && (
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Friendly Fire</span>
                  <Badge variant="destructive">
                    {flight.fratKills}
                  </Badge>
                </div>
              )}
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Mission Status</span>
                <Badge variant={flight.deaths > 0 ? "destructive" : flight.rtbCount > 0 ? "default" : "secondary"}>
                  {flight.deaths > 0 ? "KIA" : flight.rtbCount > 0 ? "RTB" : "Unknown"}
                </Badge>
              </div>
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
