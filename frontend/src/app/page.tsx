import EEGMonitor from '@/components/monitoring/EEGMonitor';
import { WebSocketProvider } from '@/contexts/WebSocketContext';
import { MonitoringProvider } from '@/contexts/MonitoringContext';

export default function Home() {
  return (
    <WebSocketProvider>
      <MonitoringProvider>
        <EEGMonitor />
      </MonitoringProvider>
    </WebSocketProvider>
  );
}