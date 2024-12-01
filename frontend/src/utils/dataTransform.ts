import { EEGData } from '../types/eeg';

export const transformForCharts = (data: EEGData[]) => {
  return data.map(d => ({
    timestamp: d.timestamp,
    attention: d.attention_metrics.attention_score,
    engagement: d.attention_metrics.engagement_index,
    thetaBetaRatio: d.attention_metrics.theta_beta_ratio
  }));
};

export const calculateBandPowerSummary = (data: EEGData) => {
  const powers = data.band_powers;
  const total = Object.values(powers).reduce((sum, val) => sum + val, 0);
  
  return Object.entries(powers).map(([band, power]) => ({
    band,
    power,
    percentage: (power / total) * 100
  }));
};