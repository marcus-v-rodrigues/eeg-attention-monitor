import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Brain } from 'lucide-react';
import { EEGData } from '@/types/eeg';

interface AttentionChartProps {
  data: EEGData[];
}

export const AttentionChart: React.FC<AttentionChartProps> = ({ data }) => {
  // Transforma os dados no formato esperado pelo gráfico
  const chartData = data.map(d => ({
    timestamp: d.timestamp,
    attention_score: d.attention_metrics.attention_score,
    engagement_index: d.attention_metrics.engagement_index
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-4 w-4" />
          Attention Levels
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                domain={['auto', 'auto']}
                tickFormatter={(time) => new Date(time * 1000).toLocaleTimeString()}
              />
              <YAxis domain={[0, 1]} />
              <Tooltip
                labelFormatter={(time) => new Date(time * 1000).toLocaleTimeString()}
                formatter={(value: number) => [(value * 100).toFixed(1) + '%']}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="attention_score"
                stroke="#8884d8"
                name="Attention"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="engagement_index"
                stroke="#82ca9d"
                name="Engagement"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};