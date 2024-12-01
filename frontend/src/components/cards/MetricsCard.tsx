import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart2 } from 'lucide-react';

interface MetricsCardProps {
  metrics: {
    thetaBetaRatio: number;
    signalQuality: number;
    artifactRatio: number;
    dominantBand: string;
    attentionTrend: 'increasing' | 'stable' | 'decreasing';
    averageAttention: number;
    averageEngagement: number;
  };
}

export const MetricsCard: React.FC<MetricsCardProps> = ({ metrics }) => {
  const getQualityColor = (value: number) => {
    if (value >= 0.8) return 'text-green-500';
    if (value >= 0.6) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getTrendIcon = () => {
    switch (metrics.attentionTrend) {
      case 'increasing':
        return '↑';
      case 'decreasing':
        return '↓';
      default:
        return '→';
    }
  };

  const getTrendColor = () => {
    switch (metrics.attentionTrend) {
      case 'increasing':
        return 'text-green-500';
      case 'decreasing':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Key Metrics</CardTitle>
        <BarChart2 className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Theta/Beta Ratio</p>
            <p className="text-2xl font-bold">
              {metrics.thetaBetaRatio.toFixed(2)}
            </p>
          </div>
          
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Signal Quality</p>
            <p className={`text-2xl font-bold ${getQualityColor(metrics.signalQuality)}`}>
              {(metrics.signalQuality * 100).toFixed(1)}%
            </p>
          </div>
          
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Artifact Ratio</p>
            <p className={`text-2xl font-bold ${getQualityColor(1 - metrics.artifactRatio)}`}>
              {(metrics.artifactRatio * 100).toFixed(1)}%
            </p>
          </div>
          
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Dominant Band</p>
            <p className="text-2xl font-bold">
              {metrics.dominantBand}
            </p>
          </div>

          <div className="col-span-2 border-t pt-4 mt-2">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm text-muted-foreground">Average Attention</p>
                  <p className="text-xl font-bold">
                    {(metrics.averageAttention * 100).toFixed(1)}%
                  </p>
                </div>
                <span className={`text-2xl ${getTrendColor()}`}>
                  {getTrendIcon()}
                </span>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">Average Engagement</p>
                <div className="flex items-center">
                  <div className="flex-1">
                    <div className="h-2 w-full bg-gray-100 rounded-full">
                      <div 
                        className="h-full bg-blue-500 rounded-full transition-all duration-500"
                        style={{ width: `${metrics.averageEngagement * 100}%` }}
                      />
                    </div>
                  </div>
                  <span className="ml-2 text-sm font-medium">
                    {(metrics.averageEngagement * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};