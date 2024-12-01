import { EEGData } from "@/types/eeg";
import { useMemo } from "react";

export function useSignalQuality(data: EEGData) {
  const quality = useMemo(() => {
    const { quality_metrics } = data;
    
    return {
      overall: quality_metrics.overall_score,
      details: {
        amplitude: quality_metrics.amplitude_ok,
        variance: quality_metrics.variance_ok,
        lineNoise: quality_metrics.line_noise_ok
      },
      status: getQualityStatus(quality_metrics.overall_score)
    };
  }, [data]);

  return quality;
}

function getQualityStatus(score: number): 'good' | 'warning' | 'poor' {
  if (score >= 0.8) return 'good';
  if (score >= 0.6) return 'warning';
  return 'poor';
}
