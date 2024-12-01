export type SessionState = 'idle' | 'recording' | 'paused' | 'analyzing';

export interface SessionInfo {
  id: string;
  startTime: number;
  duration: number;
  samplesCollected: number;
  averageAttention: number;
  signalQuality: number;
}

export interface MonitoringConfig {
  sampleRate: number;
  channelNames: string[];
  bandRanges: {
    [key: string]: [number, number];
  };
  qualityThresholds: {
    amplitude: number;
    variance: number;
    lineNoise: number;
  };
}