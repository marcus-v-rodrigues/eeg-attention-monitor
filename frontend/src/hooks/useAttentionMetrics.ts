import { useMemo } from "react";
import { EEGData } from "../types/eeg";
import { calculateAttentionTrend } from "../utils/data-processing";

export function useAttentionMetrics(data: EEGData[], windowSize = 60) {
  const metrics = useMemo(() => {
    const recentData = data.slice(-windowSize);
    
    return {
      current: data[data.length - 1]?.attention_metrics.attention_score ?? 0,
      average: calculateAverageAttention(recentData),
      trend: calculateAttentionTrend(recentData),
      engagement: data[data.length - 1]?.attention_metrics.engagement_index ?? 0
    };
  }, [data, windowSize]);

  return metrics;
}

// Utility function for average attention
function calculateAverageAttention(data: EEGData[]): number {
  if (data.length === 0) return 0;
  return data.reduce((sum, d) => sum + d.attention_metrics.attention_score, 0) / data.length;
}