import { useMemo } from 'react';
import { EEGData } from '../types/eeg';

export function useChartData(data: EEGData[], options = {}) {
  const chartData = useMemo(() => {
    return {
      attention: data.map(d => ({
        timestamp: d.timestamp,
        value: d.attention_metrics.attention_score
      })),
      bandPowers: data.map(d => ({
        timestamp: d.timestamp,
        ...d.band_powers
      })),
      connectivity: data.length > 0 ? data[data.length - 1].connectivity : undefined
    };
  }, [data]);

  return chartData;
}
