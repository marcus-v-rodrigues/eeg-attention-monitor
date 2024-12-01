from dataclasses import dataclass, field
from typing import Set, Dict, List, Optional
from collections import deque
from fastapi import WebSocket
import numpy as np
import logging
from datetime import datetime
import asyncio
import json
from src.signal_processor import EEGProcessor, SignalConfig
from src.attention_bci import AttentionBCI, BCIConfig
from src.data_loader import EEGDataLoader
from api.models.schemas import EEGDataPoint, ProcessedEEG
from pathlib import Path

logger = logging.getLogger(__name__)

class GlobalState:
    """Gerencia estado global da aplicação"""
    
    def __init__(self, buffer_size: int = 1000):
        """
        Inicializa o estado global
        
        Args:
            buffer_size: Tamanho do buffer circular
        """
        # Buffers e estado
        self.data_buffer = deque(maxlen=buffer_size)
        self.clients: Set[WebSocket] = set()
        self.session_data: List[Dict] = []
        self.is_recording = False
        
        # Métricas e estatísticas
        self.stats = {
            'total_processed': 0,
            'errors': 0,
            'last_error': None,
            'last_process_time': 0,
            'processing_times': deque(maxlen=100),  # últimos 100 tempos de processamento
            'quality_metrics': deque(maxlen=100)    # últimas 100 métricas de qualidade
        }
        
        # Componentes do sistema
        self.processor = EEGProcessor(
            SignalConfig(sfreq=128.0, buffer_size=buffer_size, window_size=int(128*0.5))
        )
        self.bci = AttentionBCI()
        self.data_loader = EEGDataLoader(buffer_size=buffer_size)

    async def process_data(self, data: Dict) -> Dict:
        try:
            # Log dos dados de entrada
            logger.info(f"Dados recebidos: {data['channels'].keys()}")
            logger.info(f"Tamanho dos canais: {[len(v) for v in data['channels'].values()]}")

            channels_data = []
            for ch in self.processor.config.channels:
                ch_data = data['channels'].get(ch, [])
                # Verifica se há dados válidos
                if not ch_data:
                    ch_data = np.random.normal(0, 0.1, self.processor.config.window_size)
                elif len(ch_data) != self.processor.config.window_size:
                    # Interpola para o tamanho correto
                    old_x = np.linspace(0, 1, len(ch_data))
                    new_x = np.linspace(0, 1, self.processor.config.window_size)
                    ch_data = np.interp(new_x, old_x, ch_data)
                channels_data.append(ch_data)
            
            channels_array = np.array(channels_data, dtype=np.float64)
            logger.info(f"Shape do array processado: {channels_array.shape}")
            
            if np.all(channels_array == 0):
                logger.error("Array contém apenas zeros após processamento")
            
            processed = await self.processor.process_async(channels_array)
            result = await self.bci.process_epoch(processed)
            
            '''
            processed_result = {
                'timestamp': data['timestamp'],
                'attention_metrics': result['attention_metrics'],
                'band_powers': {
                    band: float(power) if np.isscalar(power) else float(power[0])
                    for band, power in result['features']['band_powers'].items()
                },
                'quality_metrics': {
                    'amplitude_ok': bool(result['quality']['amplitude_ok']),
                    'variance_ok': bool(result['quality']['variance_ok']),
                    'line_noise_ok': bool(result['quality']['line_noise_ok']),
                    'overall_score': float(result['quality']['overall_score'])
                }
            }
            '''
            processed_result = {
                'timestamp': result['timestamp'],
                'attention_metrics': result['attention_metrics'],
                'band_powers': result['band_powers'],
                'connectivity': result['connectivity'],
                'quality_metrics': {
                    'amplitude_ok': str(result['quality']['amplitude_ok']),
                    'variance_ok': str(result['quality']['variance_ok']),
                    'baseline_ok': str(result['quality']['baseline_ok']),
                    'line_noise_ok': str(result['quality']['line_noise_ok']),
                    'artifact_ratio': float(result['quality']['artifact_ratio']),
                    'overall_score': float(result['quality']['overall_score'])
                }
            }
            
            self.stats['total_processed'] += 1
            return processed_result
                
        except Exception as e:
            self.stats['errors'] += 1
            self.stats['last_error'] = str(e)
            logger.error(f"Erro no processamento: {str(e)}")
            raise

    async def get_recent_data(self, seconds: float = 1.0) -> List[Dict]:
        """
        Retorna dados mais recentes
        
        Args:
            seconds: Quantidade de segundos para retornar
            
        Returns:
            Lista de dados
        """
        try:
            if not self.data_buffer:
                return []
                
            cutoff_time = datetime.now().timestamp() - seconds
            recent_data = [
                d for d in self.data_buffer 
                if d['_added_time'] > cutoff_time
            ]
            
            return recent_data
        except Exception as e:
            logger.error(f"Erro ao recuperar dados recentes: {str(e)}")
            return []
    
    def add_data(self, data: Dict) -> None:
        """Adiciona dados ao buffer"""
        self.data_buffer.append({
            **data,
            '_added_time': datetime.now().timestamp()
        })
        
        # Se estiver gravando, adiciona aos dados da sessão
        if self.is_recording:
            self.session_data.append(data)

    def get_processing_stats(self) -> Dict:
        """Retorna estatísticas de processamento"""
        return {
            'total_processed': self.stats['total_processed'],
            'errors': self.stats['errors'],
            'last_error': self.stats['last_error'],
            'quality_metrics': dict(self.stats['quality_metrics']),
            'processing_times': list(self.stats['processing_times'])
        }
    
    async def broadcast(self, message: Dict):
        """Envia mensagem para todos os clientes"""
        disconnected = set()
        for client in self.clients:
            try:
                await client.send_json(message)
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem: {str(e)}")
                disconnected.add(client)
        
        for client in disconnected:
            await self.remove_client(client)