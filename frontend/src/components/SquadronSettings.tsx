import React, { useState, useEffect } from 'react';
import { getSquadronCallsigns, updateSquadronCallsigns } from '../api';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { useToast } from '../hooks/use-toast';

export default function SquadronSettings() {
  const [callsigns, setCallsigns] = useState<string[]>([]);
  const [newCallsign, setNewCallsign] = useState('');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadCallsigns();
  }, []);

  const loadCallsigns = async () => {
    try {
      const data = await getSquadronCallsigns();
      setCallsigns(data.callsigns || []);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load squadron callsigns",
        variant: "destructive",
      });
    }
  };

  const addCallsign = () => {
    if (newCallsign.trim() && !callsigns.includes(newCallsign.trim())) {
      const updatedCallsigns = [...callsigns, newCallsign.trim()];
      setCallsigns(updatedCallsigns);
      setNewCallsign('');
      saveCallsigns(updatedCallsigns);
    }
  };

  const removeCallsign = (index: number) => {
    const updatedCallsigns = callsigns.filter((_, i) => i !== index);
    setCallsigns(updatedCallsigns);
    saveCallsigns(updatedCallsigns);
  };

  const saveCallsigns = async (callsignsToSave: string[]) => {
    setLoading(true);
    try {
      await updateSquadronCallsigns(callsignsToSave);
      toast({
        title: "Success",
        description: "Squadron callsigns updated successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update squadron callsigns",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      addCallsign();
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Squadron Callsigns</CardTitle>
        <CardDescription>
          Add your squadron's pilot callsigns. Only pilots with these callsigns flying player aircraft will be tracked.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <div className="flex-1">
            <Label htmlFor="new-callsign">Add Callsign</Label>
            <Input
              id="new-callsign"
              value={newCallsign}
              onChange={(e) => setNewCallsign(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., drunkbonsai, machinegun, bullet"
            />
          </div>
          <Button onClick={addCallsign} disabled={!newCallsign.trim() || loading}>
            Add
          </Button>
        </div>

        <div>
          <Label>Current Callsigns</Label>
          <div className="mt-2 space-y-2">
            {callsigns.length === 0 ? (
              <p className="text-sm text-muted-foreground">No callsigns configured</p>
            ) : (
              callsigns.map((callsign, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-muted rounded">
                  <span className="font-mono">{callsign}</span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => removeCallsign(index)}
                    disabled={loading}
                  >
                    Remove
                  </Button>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="text-sm text-muted-foreground">
          <p><strong>Note:</strong> The system will match callsigns in pilot names like:</p>
          <ul className="list-disc list-inside mt-1 space-y-1">
            <li><code>WILDCAT 1-1 | BULLET</code> (matches "bullet")</li>
            <li><code>MACHINEGUN - VIPER</code> (matches "machinegun")</li>
            <li><code>DRUNKBONSAI</code> (direct match)</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
} 