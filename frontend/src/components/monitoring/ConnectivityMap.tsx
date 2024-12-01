import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Brain } from 'lucide-react';

type ElectrodePosition = {
  x: number;
  y: number;
};

type ElectrodeName = 'AF3' | 'F7' | 'F3' | 'FC5' | 'T7' | 'P7' | 'O1' | 'O2' | 'P8' | 'T8' | 'FC6' | 'F4' | 'F8' | 'AF4';

const electrodePlacements: Record<ElectrodeName, ElectrodePosition> = {
  'AF3': { x: 150, y: 50 },
  'F7': { x: 80, y: 100 },
  'F3': { x: 150, y: 120 },
  'FC5': { x: 100, y: 150 },
  'T7': { x: 50, y: 200 },
  'P7': { x: 80, y: 300 },
  'O1': { x: 150, y: 350 },
  'O2': { x: 250, y: 350 },
  'P8': { x: 320, y: 300 },
  'T8': { x: 350, y: 200 },
  'FC6': { x: 300, y: 150 },
  'F4': { x: 250, y: 120 },
  'F8': { x: 320, y: 100 },
  'AF4': { x: 250, y: 50 }
};

interface ConnectivityMapProps {
  connectivityMatrix: number[][];
  channels: ElectrodeName[];
}

export const ConnectivityMap: React.FC<ConnectivityMapProps> = ({
  connectivityMatrix,
  channels
}) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-4 w-4" />
          Brain Connectivity
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative w-full aspect-square max-w-md mx-auto">
          <svg viewBox="0 0 400 400" className="w-full h-full">
            {connectivityMatrix.map((row, i) =>
              row.map((strength, j) => {
                if (j > i && strength > 0.2) {
                  const start = electrodePlacements[channels[i]];
                  const end = electrodePlacements[channels[j]];
                  return (
                    <line
                      key={`${i}-${j}`}
                      x1={start.x}
                      y1={start.y}
                      x2={end.x}
                      y2={end.y}
                      stroke={`rgba(59, 130, 246, ${strength})`}
                      strokeWidth={strength * 4}
                    />
                  );
                }
                return null;
              })
            )}
            
            {channels.map((channel, i) => {
              const pos = electrodePlacements[channel];
              return (
                <g key={channel}>
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r="12"
                    fill="white"
                    stroke="rgb(209 213 219)"
                  />
                  <text
                    x={pos.x}
                    y={pos.y}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="text-xs font-medium fill-gray-700"
                  >
                    {channel}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
      </CardContent>
    </Card>
  );
};