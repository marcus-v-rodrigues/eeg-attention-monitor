import { EEGData, BandPowers } from '../types/eeg';

export function calculateAttentionTrend(
  historicalData: EEGData[],
  windowSize: number = 10
): 'increasing' | 'stable' | 'decreasing' {
  if (historicalData.length < windowSize) return 'stable';

  const recentData = historicalData.slice(-windowSize);
  const midPoint = Math.floor(windowSize / 2);
  
  const firstHalf = recentData.slice(0, midPoint);
  const secondHalf = recentData.slice(midPoint);

  const firstAvg = firstHalf.reduce((sum, d) => sum + d.attention_metrics.attention_score, 0) / midPoint;
  const secondAvg = secondHalf.reduce((sum, d) => sum + d.attention_metrics.attention_score, 0) / midPoint;

  const difference = secondAvg - firstAvg;
  
  if (difference > 0.05) return 'increasing';
  if (difference < -0.05) return 'decreasing';
  return 'stable';
}

export function getDominantBand(bandPowers: BandPowers): string {
  return Object.entries(bandPowers).reduce((max, [band, power]) => 
    power > max.power ? { band, power } : max,
    { band: '', power: -Infinity }
  ).band;
}

export function calculateEngagementIndex(bandPowers: BandPowers): number {
  const { beta, alpha, theta } = bandPowers;
  return beta / (alpha + theta);
}