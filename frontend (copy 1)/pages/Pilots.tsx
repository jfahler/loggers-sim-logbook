import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Users, Plane, Target, Skull, Clock, Send, AlertTriangle } from 'lucide-react';
import backend from '~backend/client';

export function Pilots() {
  const { toast } = useToast();

  const { data: pilots, isLoading } = useQuery({
    queryKey: ['pilots'],
    queryFn: () => backend.logbook.listPilots(),
  });

  const sendStatsMutation = useMutation({
    mutationFn: (pilot: any) => backend.discord.sendPilotStats({
      pilotName: pilot.pilot.name,
      pilotCallsign: pilot.pilot.callsign || null,
      totalFlights: pilot.totalFlights,
      totalFlightTime: pilot.totalFlightTime,
      totalAaKills: pilot.totalAaKills,
      totalAgKills: pilot.totalAgKills,
      totalFratKills: pilot.totalFratKills,
      totalRtbCount: pilot.totalRtbCount,
      totalEjections: pilot.totalEjections,
      totalDeaths: pilot.totalDeaths,
      favoriteAircraft: pilot.favoriteAircraft,
      averageFlightDuration: pilot.averageFlightDuration,
    }),
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
      console.error('Error sending pilot stats:', error);
      toast({
        title: "Error",
        description: "Failed to send pilot statistics to Discord",
        variant: "destructive",
      });
    },
  });

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  };

  const getKillDeathRatio = (aaKills: number, agKills: number, deaths: number) => {
    const totalKills = aaKills + agKills;
    if (deaths === 0) return totalKills.toString();
    return (totalKills / deaths).toFixed(2);
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading pilots...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Pilots</h1>
        <p className="text-gray-600 mt-2">View pilot statistics and performance</p>
      </div>

      <div className="grid gap-6">
        {pilots?.pilots.map((pilot) => (
          <Card key={pilot.pilot.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-xl">
                    {pilot.pilot.callsign ? `${pilot.pilot.name} (${pilot.pilot.callsign})` : pilot.pilot.name}
                  </CardTitle>
                  <p className="text-gray-600">
                    Joined {new Date(pilot.pilot.createdAt).toLocaleDateString()}
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => sendStatsMutation.mutate(pilot)}
                  disabled={sendStatsMutation.isPending}
                >
                  <Send className="h-4 w-4 mr-2" />
                  Send to Discord
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="flex items-center space-x-2">
                  <Plane className="h-4 w-4 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-600">Total Flights</p>
                    <p className="font-semibold">{pilot.totalFlights}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-green-600" />
                  <div>
                    <p className="text-sm text-gray-600">Flight Time</p>
                    <p className="font-semibold">{formatDuration(pilot.totalFlightTime)}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Target className="h-4 w-4 text-red-600" />
                  <div>
                    <p className="text-sm text-gray-600">Total Kills</p>
                    <p className="font-semibold">{pilot.totalAaKills + pilot.totalAgKills}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Skull className="h-4 w-4 text-gray-600" />
                  <div>
                    <p className="text-sm text-gray-600">Deaths</p>
                    <p className="font-semibold">{pilot.totalDeaths}</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="flex items-center space-x-2">
                  <Target className="h-4 w-4 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-600">A-A Kills</p>
                    <p className="font-semibold">{pilot.totalAaKills}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Target className="h-4 w-4 text-green-600" />
                  <div>
                    <p className="text-sm text-gray-600">A-G Kills</p>
                    <p className="font-semibold">{pilot.totalAgKills}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4 text-orange-600" />
                  <div>
                    <p className="text-sm text-gray-600">Friendly Kills</p>
                    <p className="font-semibold">{pilot.totalFratKills}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Plane className="h-4 w-4 text-purple-600" />
                  <div>
                    <p className="text-sm text-gray-600">RTB Count</p>
                    <p className="font-semibold">{pilot.totalRtbCount}</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-600">K/D Ratio</p>
                  <Badge variant="outline" className="mt-1">
                    {getKillDeathRatio(pilot.totalAaKills, pilot.totalAgKills, pilot.totalDeaths)}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Favorite Aircraft</p>
                  <Badge variant="secondary" className="mt-1">
                    {pilot.favoriteAircraft}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Avg Flight Duration</p>
                  <Badge variant="outline" className="mt-1">
                    {formatDuration(pilot.averageFlightDuration)}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Ejections</p>
                  <Badge variant={pilot.totalEjections > 0 ? "secondary" : "outline"} className="mt-1">
                    {pilot.totalEjections}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {pilots?.pilots.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No pilots found. Upload some Tacview files to get started!</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
