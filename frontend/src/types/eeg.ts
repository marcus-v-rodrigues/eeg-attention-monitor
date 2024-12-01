export interface BandPowers {
  delta: number;
  theta: number;
  alpha: number;
  beta: number;
  gamma: number;
}

export interface AttentionMetrics {
  attention_score: number;
  engagement_index: number;
  theta_beta_ratio: number;
  eye_state: 'open' | 'closed';
}

export interface QualityMetrics {
  amplitude_ok: boolean;
  variance_ok: boolean;
  line_noise_ok: boolean;
  baseline_ok: boolean;
  overall_score: number;
  artifact_ratio: number;
}

export type ElectrodeName = 'AF3' | 'F7' | 'F3' | 'FC5' | 'T7' | 'P7' | 'O1' | 'O2' | 'P8' | 'T8' | 'FC6' | 'F4' | 'F8' | 'AF4';

export interface EEGData {
  timestamp: number;
  channels: Record<ElectrodeName, number[]>;
  band_powers: BandPowers;
  attention_metrics: AttentionMetrics;
  quality_metrics: QualityMetrics;
  connectivity?: number[][];
}
export interface ProcessedData {
  data: EEGData;
  status: 'success' | 'error';
  message?: string;
}
