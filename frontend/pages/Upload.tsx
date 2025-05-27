import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { useToast } from '@/hooks/use-toast';
import { Upload as UploadIcon, FileText, Send } from 'lucide-react';
import backend from '~backend/client';

export function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [sendToDiscord, setSendToDiscord] = useState(true);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: async (fileData: { filename: string; fileData: string }) => {
      return backend.logbook.uploadTacview(fileData);
    },
    onSuccess: async (data) => {
      toast({
        title: "Success",
        description: data.message,
      });
      
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['flights'] });
      queryClient.invalidateQueries({ queryKey: ['pilots'] });
      
      // Send to Discord if requested
      if (sendToDiscord && data.flightId) {
        try {
          const flight = await backend.logbook.getFlight({ id: data.flightId });
          await backend.discord.sendFlightSummary({
            flightId: flight.id,
            pilotName: flight.pilotName,
            pilotCallsign: flight.pilotCallsign,
            aircraftType: flight.aircraftType,
            missionName: flight.missionName,
            startTime: flight.startTime,
            durationSeconds: flight.durationSeconds,
            kills: flight.kills,
            deaths: flight.deaths,
            maxAltitudeFeet: flight.maxAltitudeFeet,
            maxSpeedKnots: flight.maxSpeedKnots,
            distanceNm: flight.distanceNm,
          });
          
          toast({
            title: "Discord Notification",
            description: "Flight summary sent to Discord successfully",
          });
        } catch (error) {
          console.error('Error sending to Discord:', error);
          toast({
            title: "Discord Error",
            description: "Failed to send flight summary to Discord",
            variant: "destructive",
          });
        }
      }
      
      setFile(null);
    },
    onError: (error) => {
      console.error('Upload error:', error);
      toast({
        title: "Upload Failed",
        description: "Failed to upload and process the Tacview file",
        variant: "destructive",
      });
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      const reader = new FileReader();
      
      reader.onload = () => {
        const result = reader.result as string;
        // Extract base64 data from data URL (remove "data:application/octet-stream;base64," prefix)
        const base64Data = result.split(',')[1];
        
        uploadMutation.mutate({
          filename: file.name,
          fileData: base64Data,
        });
      };
      
      reader.onerror = () => {
        toast({
          title: "File Error",
          description: "Failed to read the selected file",
          variant: "destructive",
        });
      };
      
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Error reading file:', error);
      toast({
        title: "File Error",
        description: "Failed to read the selected file",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload Tacview File</h1>
        <p className="text-gray-600 mt-2">Upload a Tacview (.acmi) file to track your DCS flight statistics</p>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <UploadIcon className="h-5 w-5" />
            <span>File Upload</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="tacview-file">Select Tacview File</Label>
            <Input
              id="tacview-file"
              type="file"
              accept=".acmi,.txt"
              onChange={handleFileChange}
              disabled={uploadMutation.isPending}
            />
            <p className="text-sm text-gray-600">
              Supported formats: .acmi, .txt (Tacview files)
            </p>
          </div>

          {file && (
            <div className="flex items-center space-x-2 p-3 bg-gray-50 rounded-md">
              <FileText className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium">{file.name}</span>
              <span className="text-sm text-gray-500">
                ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </span>
            </div>
          )}

          <div className="flex items-center space-x-2">
            <Checkbox
              id="send-discord"
              checked={sendToDiscord}
              onCheckedChange={(checked) => setSendToDiscord(checked as boolean)}
            />
            <Label htmlFor="send-discord" className="flex items-center space-x-2">
              <Send className="h-4 w-4" />
              <span>Send flight summary to Discord</span>
            </Label>
          </div>

          <Button
            onClick={handleUpload}
            disabled={!file || uploadMutation.isPending}
            className="w-full"
          >
            {uploadMutation.isPending ? (
              "Processing..."
            ) : (
              <>
                <UploadIcon className="h-4 w-4 mr-2" />
                Upload and Process
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>How it works</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <h4 className="font-medium">1. Export from DCS</h4>
            <p className="text-sm text-gray-600">
              Enable Tacview in DCS and fly your mission. Tacview files are automatically saved to your DCS folder.
            </p>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium">2. Upload File</h4>
            <p className="text-sm text-gray-600">
              Select and upload your .acmi file. The system will automatically parse flight data including pilot info, aircraft type, kills, deaths, and flight statistics.
            </p>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium">3. View Statistics</h4>
            <p className="text-sm text-gray-600">
              Browse your flight history, pilot statistics, and optionally share summaries with your Discord group.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
