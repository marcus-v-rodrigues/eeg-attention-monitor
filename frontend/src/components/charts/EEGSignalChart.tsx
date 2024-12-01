import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Wave } from 'lucide-react';

interface EEGSignalChartProps {
  data: Array<{
    timestamp: number;
    channels: Record<string, number>;
  }>;
  selectedChannels?: string[];
}

export const EEGSignalChart: React.FC<EEGSignalChartProps> = ({ 
  data,
  selectedChannels = ['AF3', 'AF4', 'F3', 'F4']
}) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Wave className="h-4 w-4" />
          EEG Signal
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="timestamp"
                domain={['auto', 'auto']}
                tickFormatter={(time) => new Date(time * 1000).toLocaleTimeString()}
              />
              <YAxis />
              <Tooltip
                labelFormatter={(time) => new Date(time * 1000).toLocaleTimeString()}
              />
              <Legend />
              {selectedChannels.map((channel, index) => (
                <Line
                  key={channel}
                  type="monotone"
                  dataKey={`channels.${channel}`}
                  stroke={`hsl(${(index * 360) / selectedChannels.length}, 70%, 50%)`}
                  name={channel}
                  dot={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};