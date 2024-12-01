import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Activity } from 'lucide-react';

interface BandPowerChartProps {
  data: {
    delta: number;
    theta: number;
    alpha: number;
    beta: number;
    gamma: number;
  };
}

type BandType = 'delta' | 'theta' | 'alpha' | 'beta' | 'gamma';

type BandColors = {
  [key in BandType]: string;
};

interface DataPoint {
  timestamp: number;
  delta: number;
  theta: number;
  alpha: number;
  beta: number;
  gamma: number;
}

export const BandPowerChart: React.FC<BandPowerChartProps> = ({ data }) => {
  const [chartData, setChartData] = useState<DataPoint[]>([]);

  const bandColors: BandColors = {
    delta: '#1f77b4',
    theta: '#ff7f0e',
    alpha: '#2ca02c',
    beta: '#d62728',
    gamma: '#9467bd'
  };

  const bands: BandType[] = ['delta', 'theta', 'alpha', 'beta', 'gamma'];

  // Initialize chart data if empty
  useEffect(() => {
    if (chartData.length === 0) {
      const now = Date.now();
      const initialData: DataPoint[] = Array.from({ length: 100 }, (_, i) => ({
        timestamp: now - (100 - i) * 100,
        delta: 0,
        theta: 0,
        alpha: 0,
        beta: 0,
        gamma: 0
      }));
      setChartData(initialData);
    }
  }, []);

  // Update chart data with new values
  useEffect(() => {
    const newDataPoint: DataPoint = {
      timestamp: Date.now(),
      ...data
    };

    setChartData(prev => {
      // Remove first point and add new point at the end
      return [...prev.slice(1), newDataPoint];
    });
  }, [data]);

  return (
    <Card className="h-96">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-4 w-4" />
          Frequency Band Powers
        </CardTitle>
      </CardHeader>
      <CardContent className="h-[calc(100%-5rem)]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ right: 30, left: 20, top: 5, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="timestamp"
              type="number"
              domain={['auto', 'auto']}
              scale="time"
              tickFormatter={(timestamp) => {
                const date = new Date(timestamp);
                return date.toLocaleTimeString('en-US', {
                  hour12: false,
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit'
                });
              }}
              tick={{ fontSize: 11 }}
              minTickGap={50}
            />
            <YAxis 
              domain={[0, 0.8]}
              tickCount={5}
              tick={{ fontSize: 11 }}
            />
            <Tooltip 
              labelFormatter={(timestamp) => {
                const date = new Date(timestamp);
                return date.toLocaleTimeString('en-US', {
                  hour12: false,
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                  fractionalSecondDigits: 3
                });
              }}
            />
            <Legend 
              verticalAlign="top"
              align="right"
              height={36}
              iconType="plainline"
              iconSize={16}
            />
            {bands.map((band) => (
              <Line
                key={band}
                type="monotone"
                dataKey={band}
                stroke={bandColors[band]}
                name={band.charAt(0).toUpperCase() + band.slice(1)}
                dot={false}
                strokeWidth={2}
                isAnimationActive={false}
                connectNulls={true}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default BandPowerChart;