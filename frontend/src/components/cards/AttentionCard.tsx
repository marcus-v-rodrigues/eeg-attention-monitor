import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity } from 'lucide-react';

interface AttentionCardProps {
  attentionScore: number;
  engagementIndex: number;
}

export const AttentionCard: React.FC<AttentionCardProps> = ({ 
  attentionScore,
  engagementIndex
}) => {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Attention Level</CardTitle>
        <Activity className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="flex flex-col space-y-4">
          <div>
            <p className="text-sm text-muted-foreground">Attention Score</p>
            <div className="flex items-center">
              <div className="flex-1">
                <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500 transition-all duration-500"
                    style={{ width: `${attentionScore * 100}%` }}
                  />
                </div>
              </div>
              <span className="ml-2 text-sm font-medium">
                {(attentionScore * 100).toFixed(1)}%
              </span>
            </div>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground">Engagement Index</p>
            <div className="flex items-center">
              <div className="flex-1">
                <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-green-500 transition-all duration-500"
                    style={{ width: `${engagementIndex * 100}%` }}
                  />
                </div>
              </div>
              <span className="ml-2 text-sm font-medium">
                {(engagementIndex * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};