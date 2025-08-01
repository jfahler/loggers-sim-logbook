import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { useToast } from '@/hooks/use-toast';
import { Upload as UploadIcon, FileText, Send } from 'lucide-react';
import api from '@/api';

export function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [sendToDiscord, setSendToDiscord] = useState(true);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: async (uploadFile: File) => {
      console.log('Starting upload mutation with file:', uploadFile.name);

      try {
        const result = await api.uploadXml(uploadFile);
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
        
        // Re-throw the original error to be handled by onError
        throw error;
      }
    },
    onSuccess: async (data) => {
      console.log('Upload mutation success:', data);
      
      // Show enhanced success message with pilot information
      const pilotCount = data.pilots_updated || 'unknown';
      toast({
        title: "XML Processing Complete",
        description: `Successfully processed ${pilotCount} pilot profiles with enhanced tracking including flight hours, kills, and platform statistics.`,
      });
      
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['flights'] });
      queryClient.invalidateQueries({ queryKey: ['pilots'] });
      
      // Send to Discord if requested
      if (sendToDiscord && data.flightId) {
        try {
          console.log('Fetching flight details for Discord:', data.flightId);
          const flight = await api.getFlight(data.flightId);

          console.log('Sending to Discord:', flight);
          await api.sendFlightSummary({
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
      
      let errorMessage = "Failed to upload and process the XML file";
      
      // Handle different types of errors
      if (error?.message) {
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError') || error.message.includes('fetch')) {
          errorMessage = "Network error: Unable to connect to the server. Please check your internet connection and try again.";
        } else if (error.message.includes('filename and fileData are required')) {
          errorMessage = "Invalid file data. Please try selecting the file again.";
        } else if (error.message.includes('invalid base64 file data')) {
          errorMessage = "File format error. Please ensure you're uploading a valid XML file.";
        } else if (error.message.includes('file size exceeds')) {
          errorMessage = "File is too large. Please select a file smaller than 50MB.";
        } else if (error.message.includes('file must have .xml extension')) {
          errorMessage = "Invalid file type. Please select a .xml file.";
        } else if (error.message.includes('could not extract pilot name')) {
          errorMessage = "Unable to parse pilot information from the file. Please ensure it's a valid Tacview XML file.";
        } else if (error.message.includes('could not extract aircraft type')) {
          errorMessage = "Unable to parse aircraft information from the file. Please ensure it's a valid Tacview XML file.";
        } else {
          errorMessage = error.message;
        }
      } else if (error?.body?.message) {
        errorMessage = error.body.message;
      } else if (error?.code) {
        // Handle API error codes
        switch (error.code) {
          case 'invalid_argument':
            errorMessage = error.message || "Invalid file or request data";
            break;
          case 'internal':
            errorMessage = "Server error occurred while processing the file";
            break;
          case 'not_found':
            errorMessage = "Upload endpoint not found";
            break;
          default:
            errorMessage = error.message || "An unexpected error occurred";
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
      const validExtensions = ['.xml'];
      const fileExtension = selectedFile.name.toLowerCase().substring(selectedFile.name.lastIndexOf('.'));
      if (!validExtensions.includes(fileExtension)) {
        toast({
          title: "Invalid File Type",
          description: "Please select a .xml file",
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
      console.log('Calling upload mutation...');
      uploadMutation.mutate(file);
    } catch (error) {
      console.error('Upload error:', error);
      toast({
        title: "Upload Error",
        description: "Failed to upload the selected file.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload Tacview XML File</h1>
        <p className="text-gray-600 mt-2">Upload a Tacview XML file to track your DCS flight statistics</p>
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
            <Label htmlFor="tacview-file">Select Tacview XML File</Label>
            <Input
              id="tacview-file"
              type="file"
              accept=".xml"
              onChange={handleFileChange}
              disabled={uploadMutation.isPending}
            />
            <p className="text-sm text-gray-600">
              Supported formats: .xml (Tacview XML files) • Max size: 50MB
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
          <CardTitle>XML Processing Benefits</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <h4 className="font-medium">What we track:</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Number of flights per pilot</li>
              <li>• Air-to-Air kills</li>
              <li>• Air-to-Ground kills</li>
              <li>• Friendly fire incidents</li>
              <li>• Return to base (RTB) events</li>
              <li>• Ejections</li>
              <li>• Deaths/KIA</li>
              <li>• Flight duration and basic info</li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium">XML Advantages:</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Faster processing of large files</li>
              <li>• Reduced storage requirements</li>
              <li>• Focus on key combat statistics</li>
              <li>• Simplified Discord notifications</li>
              <li>• Better compatibility with Tacview exports</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
