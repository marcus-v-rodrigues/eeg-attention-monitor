import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PlayCircle, StopCircle, Save, Upload } from 'lucide-react';

interface SessionControlsProps {
  isRecording: boolean;
  onStartRecording: () => void;
  onStopRecording: () => void;
  onSaveSession: () => void;
  onLoadSession: () => void;
  disabled?: boolean;
}

export const SessionControls: React.FC<SessionControlsProps> = ({
  isRecording,
  onStartRecording,
  onStopRecording,
  onSaveSession,
  onLoadSession,
  disabled
}) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Session Controls</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-4">
          <Button
            variant={isRecording ? "secondary" : "default"}
            onClick={isRecording ? onStopRecording : onStartRecording}
            disabled={disabled}
            className="flex items-center gap-2"
          >
            {isRecording ? (
              <>
                <StopCircle className="h-4 w-4" />
                Stop Recording
              </>
            ) : (
              <>
                <PlayCircle className="h-4 w-4" />
                Start Recording
              </>
            )}
          </Button>
          
          <Button
            variant="outline"
            onClick={onSaveSession}
            disabled={!isRecording || disabled}
            className="flex items-center gap-2"
          >
            <Save className="h-4 w-4" />
            Save Session
          </Button>
          
          <Button
            variant="outline"
            onClick={onLoadSession}
            disabled={isRecording || disabled}
            className="flex items-center gap-2"
          >
            <Upload className="h-4 w-4" />
            Load Session
          </Button>
        </div>

        {isRecording && (
          <div className="mt-4 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            <span className="text-sm text-gray-500">Recording in progress...</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};