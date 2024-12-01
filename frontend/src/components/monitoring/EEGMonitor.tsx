"use client";

import React from 'react';
import { useWebSocketContext } from '@/contexts/WebSocketContext';
import { useMonitoringContext } from '@/contexts/MonitoringContext';
import dynamic from 'next/dynamic';
import { Dashboard } from '@/components/layout/Dashboard';
import { type ElectrodeName } from "@/types/eeg";
import { ConnectivityMap } from '@/components/monitoring/ConnectivityMap';

// Create dynamic components with correct types
const DynamicAttentionCard = dynamic(() => 
  import('@/components/cards/AttentionCard').then(mod => mod.AttentionCard), 
  { ssr: false }
);

const DynamicMetricsCard = dynamic(() => 
  import('@/components/cards/MetricsCard').then(mod => mod.MetricsCard), 
  { ssr: false }
);

const DynamicStateCard = dynamic(() => 
  import('@/components/cards/StateCard').then(mod => mod.StateCard), 
  { ssr: false }
);

const DynamicAttentionChart = dynamic(() => 
  import('@/components/charts/AttentionChart').then(mod => mod.AttentionChart), 
  { ssr: false }
);

const DynamicBandPowerChart = dynamic(() => 
  import('@/components/charts/BandPowerChart').then(mod => mod.BandPowerChart), 
  { ssr: false }
);

const DynamicQualityIndicator = dynamic(() => 
  import('@/components/monitoring/QualityIndicator').then(mod => mod.QualityIndicator), 
  { ssr: false }
);

const EEGMonitor = () => {
  const { state } = useMonitoringContext();
  const { isConnected } = useWebSocketContext();

  if (!state.currentData) {
    return (
      <Dashboard>
        <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
          <div className="text-center">
            <h2 className="text-xl font-semibold mb-2">Aguardando dados...</h2>
            <p className="text-muted-foreground">
              {isConnected ? 'Conectado, aguardando sinais EEG' : 'Tentando conectar ao servidor'}
            </p>
          </div>
        </div>
      </Dashboard>
    );
  }

  const { attention_metrics, band_powers, quality_metrics } = state.currentData;

  const metrics = {
    thetaBetaRatio: attention_metrics.theta_beta_ratio,
    signalQuality: quality_metrics.overall_score,
    artifactRatio:  quality_metrics.artifact_ratio || 0,
    dominantBand: Object.entries(band_powers).reduce(
      (max, [band, power]) => power > max.power ? {band, power} : max, 
      {band: '', power: -Infinity}
    ).band,
    attentionTrend: state.attentionMetrics.trend,
    averageAttention: state.attentionMetrics.average,
    averageEngagement: attention_metrics.engagement_index
  };

  return (
    <Dashboard>
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
        <DynamicStateCard 
          eyeState={attention_metrics.eye_state}
          attentionScore={attention_metrics.attention_score}
        />
        <DynamicAttentionCard 
          attentionScore={attention_metrics.attention_score}
          engagementIndex={attention_metrics.engagement_index}
        />
        <DynamicQualityIndicator metrics={{
          amplitudeOk: quality_metrics.amplitude_ok,
          varianceOk: quality_metrics.variance_ok,
          lineNoiseOk: quality_metrics.line_noise_ok,
          overallScore: quality_metrics.overall_score
        }} />
        <DynamicMetricsCard metrics={metrics} />
      </div>

      <div className="grid gap-4 mt-4 grid-cols-1 lg:grid-cols-2">
        <DynamicAttentionChart data={state.historicalData} />
        <DynamicBandPowerChart data={band_powers} />
        {state.currentData.connectivity && (
          <ConnectivityMap 
            connectivityMatrix={state.currentData.connectivity}
            channels={state.config.channels as ElectrodeName[]}
          />
      )}
      </div>
    </Dashboard>
  );
};

export default EEGMonitor;