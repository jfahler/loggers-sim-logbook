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
      console.log('Starting upload mutation with:', {
        filename: fileData.filename,
        dataLength: fileData.fileData.length
      });

      try {
        const result = await backend.logbook.uploadTacview(fileData);
        console.log('Upload successful:', result);
        return result;
      } catch (error: any) {
        console.error('Upload API error details:', {
          error,
          message: error?.message,
          body: error?.body,
          status: error?.status,
          stack: error?.stack
        });
        
        // Handle different types of errors
        if (error?.message?.includes('Failed to fetch')) {
          throw new Error('Network error: Unable to connect to the server. Please check your internet connection and try again.');
        }
        
        if (error?.body?.message) {
          throw new Error(error.body.message);
        }
        
        if (error?.message) {
          throw new Error(error.message);
        }
        
        throw new Error('An unexpected error occurred while uploading the file');
      }
    },
    onSuccess: async (data) => {
      console.log('Upload mutation success:', data);
      
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
          console.log('Fetching flight details for Discord:', data.flightId);
          const flight = await backend.logbook.getFlight({ id: data.flightId });
          
          console.log('Sending to Discord:', flight);
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
      // Reset the file input
      const fileInput = document.getElementById('tacview-file') as HTMLInputElement;
      if (fileInput) {
        fileInput.value = '';
      }
    },
    onError: (error: any) => {
      console.error('Upload mutation error:', error);
      
      let errorMessage = "Failed to upload and process the Tacview file";
      
      // Try to extract more specific error information
      if (error?.message) {
        if (error.message.includes('Network error')) {
          errorMessage = error.message;
        } else if (error.message.includes('filename and fileData are required')) {
          errorMessage = "Invalid file data. Please try selecting the file again.";
        } else if (error.message.includes('invalid base64 file data')) {
          errorMessage = "File format error. Please ensure you're uploading a valid Tacview file.";
        } else if (error.message.includes('file size exceeds')) {
          errorMessage = "File is too large. Please select a file smaller than 50MB.";
        } else if (error.message.includes('file must have .acmi or .txt extension')) {
          errorMessage = "Invalid file type. Please select a .acmi or .txt file.";
        } else if (error.message.includes('could not extract pilot name')) {
          errorMessage = "Unable to parse pilot information from the file. Please ensure it's a valid Tacview file.";
        } else if (error.message.includes('could not extract aircraft type')) {
          errorMessage = "Unable to parse aircraft information from the file. Please ensure it's a valid Tacview file.";
        } else {
          errorMessage = error.message;
        }
      }
      
      toast({
        title: "Upload Failed",
        description: errorMessage,
        variant: "destructive",
      });
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      console.log('File selected:', {
        name: selectedFile.name,
        size: selectedFile.size,
        type: selectedFile.type
      });
      
      // Validate file size (max 50MB)
      if (selectedFile.size > 50 * 1024 * 1024) {
        toast({
          title: "File Too Large",
          description: "Please select a file smaller than 50MB",
          variant: "destructive",
        });
        return;
      }
      
      // Validate file extension
      const validExtensions = ['.acmi', '.txt'];
      const fileExtension = selectedFile.name.toLowerCase().substring(selectedFile.name.lastIndexOf('.'));
      if (!validExtensions.includes(fileExtension)) {
        toast({
          title: "Invalid File Type",
          description: "Please select a .acmi or .txt file",
          variant: "destructive",
        });
        return;
      }
      
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast({
        title: "No File Selected",
        description: "Please select a file to upload",
        variant: "destructive",
      });
      return;
    }

    console.log('Starting file upload process for:', file.name);

    try {
      const reader = new FileReader();
      
      reader.onload = () => {
        try {
          const result = reader.result as string;
          
          if (!result) {
            throw new Error('Failed to read file');
          }
          
          console.log('File read successfully, data URL length:', result.length);
          
          // Extract base64 data from data URL (remove "data:application/octet-stream;base64," prefix)
          const base64Data = result.split(',')[1];
          
          if (!base64Data || base64Data.trim().length === 0) {
            throw new Error('Failed to extract file data');
          }
          
          console.log('Base64 data extracted, length:', base64Data.length);
          
          // Validate the filename
          if (!file.name || file.name.trim().length === 0) {
            throw new Error('Invalid filename');
          }
          
          // Test if the base64 data is valid
          try {
            const testBuffer = Buffer.from(base64Data, 'base64');
            console.log('Base64 validation successful, buffer size:', testBuffer.length);
          } catch (base64Error) {
            console.error('Base64 validation failed:', base64Error);
            throw new Error('Invalid file encoding');
          }
          
          console.log('Calling upload mutation...');
          uploadMutation.mutate({
            filename: file.name.trim(),
            fileData: base64Data,
          });
        } catch (error) {
          console.error('Error processing file data:', error);
          toast({
            title: "File Processing Error",
            description: "Failed to process the selected file. Please try again.",
            variant: "destructive",
          });
        }
      };
      
      reader.onerror = (error) => {
        console.error('FileReader error:', error);
        toast({
          title: "File Error",
          description: "Failed to read the selected file. Please try again.",
          variant: "destructive",
        });
      };
      
      console.log('Starting file read...');
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Error reading file:', error);
      toast({
        title: "File Error",
        description: "Failed to read the selected file. Please try again.",
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
              Supported formats: .acmi, .txt (Tacview files) • Max size: 50MB
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

      {process.env.NODE_ENV === 'development' && (
        <Card className="max-w-2xl border-yellow-200 bg-yellow-50">
          <CardHeader>
            <CardTitle className="text-yellow-800">Debug Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <p><strong>Upload Status:</strong> {uploadMutation.isPending ? 'In Progress' : 'Ready'}</p>
              <p><strong>File Selected:</strong> {file ? `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)` : 'None'}</p>
              <p><strong>Send to Discord:</strong> {sendToDiscord ? 'Yes' : 'No'}</p>
              {uploadMutation.error && (
                <div className="mt-2 p-2 bg-red-100 border border-red-200 rounded">
                  <p className="text-red-800"><strong>Last Error:</strong></p>
                  <pre className="text-xs text-red-700 whitespace-pre-wrap">
                    {JSON.stringify(uploadMutation.error, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
