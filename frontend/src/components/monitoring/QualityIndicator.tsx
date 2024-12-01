import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Signal } from 'lucide-react';

interface QualityIndicatorProps {
  metrics: {
    amplitudeOk: boolean;
    varianceOk: boolean;
    lineNoiseOk: boolean;
    overallScore: number;
  };
}

export const QualityIndicator: React.FC<QualityIndicatorProps> = ({ metrics }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Signal className="h-4 w-4" />
          Signal Quality
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Indicadores de qualidade */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                metrics.amplitudeOk ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <span className="text-sm">Amplitude</span>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                metrics.varianceOk ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <span className="text-sm">Variance</span>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                metrics.lineNoiseOk ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <span className="text-sm">Line Noise</span>
            </div>
          </div>

          {/* Barra de qualidade geral */}
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-sm">Overall Quality</span>
              <span className="text-sm font-medium">
                {(metrics.overallScore * 100).toFixed(1)}%
              </span>
            </div>
            <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-green-500 transition-all duration-500"
                style={{ width: `${metrics.overallScore * 100}%` }}
              />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
