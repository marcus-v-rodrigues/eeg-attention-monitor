export const MONITORING_CONFIG = {
  refreshRate: 128, // Hz
  bufferSize: 1000, // amostras
  channels: [
    'AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1',
    'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4'
  ],
  bandRanges: {
    delta: [0.5, 4] as [number, number],
    theta: [4, 8] as [number, number],
    alpha: [8, 13] as [number, number],
    beta: [13, 30] as [number, number],
    gamma: [30, 45] as [number, number]
  } as const,
  qualityThresholds: {
    amplitude: 100, // µV
    variance: 0.1,
    lineNoise: 0.2
  },
  visualization: {
    colors: {
      attention: '#8884d8',
      engagement: '#82ca9d',
      delta: '#4E79A7',
      theta: '#F28E2B',
      alpha: '#E15759',
      beta: '#76B7B2',
      gamma: '#59A14F'
    },
    chartDefaults: {
      height: 300,
      margin: { top: 20, right: 30, left: 20, bottom: 30 }
    }
  }
};