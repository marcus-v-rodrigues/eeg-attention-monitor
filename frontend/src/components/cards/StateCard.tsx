import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Eye, EyeOff } from 'lucide-react';

interface StateCardProps {
  eyeState: 'open' | 'closed';
  attentionScore: number;
}

export const StateCard: React.FC<StateCardProps> = ({ eyeState, attentionScore }) => {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Current State</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          {eyeState === 'open' ? (
            <Eye className="h-8 w-8 text-green-500" />
          ) : (
            <EyeOff className="h-8 w-8 text-red-500" />
          )}
          <div className="text-right">
            <p className="text-2xl font-bold">
              {eyeState === 'open' ? 'Eyes Open' : 'Eyes Closed'}
            </p>
            <p className="text-xs text-muted-foreground">
              Attention: {(attentionScore * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};