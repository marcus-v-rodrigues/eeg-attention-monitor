import numpy as np
from datetime import datetime
import logging
from dataclasses import dataclass, field
from scipy import signal
import pywt
from typing import Dict, Optional, List, Tuple
import logging
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class SignalConfig:
    """Configurações para processamento de sinais"""
    sfreq: float = 128.0
    notch_freq: float = 60.0
    bandpass_low: float = 0.5
    bandpass_high: float = 45.0
    artifact_threshold: float = 100.0
    window_size: int = 128  # 1 segundo
    overlap: float = 0.5
    buffer_size: int = 1000
    channels: List[str] = field(default_factory=lambda: [
        'AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1',
        'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4'
    ])
    
class EEGProcessor:
    def __init__(self, config: Optional[SignalConfig] = None):
        """
        Inicializa o processador
        
        Args:
            config: Configurações do processador
        """
        self.config = config or SignalConfig()
        self._init_filters()
        
    def _init_filters(self):
        """Inicializa filtros"""
        nyq = self.config.sfreq / 2
        
        # Filtro Notch para 60Hz
        notch_freq = self.config.notch_freq / nyq
        self.notch_b, self.notch_a = signal.iirnotch(
            notch_freq,
            Q=30.0
        )
        
        # Filtro passa-banda
        low = self.config.bandpass_low / nyq
        high = self.config.bandpass_high / nyq
        self.bandpass_b, self.bandpass_a = signal.butter(
            4, [low, high],
            btype='band'
        )
        
        # Filtros para bandas específicas
        self.band_filters = {}
        for band, (low, high) in {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 45)
        }.items():
            b, a = signal.butter(
                4,
                [low/nyq, high/nyq],
                btype='band'
            )
            self.band_filters[band] = (b, a)
    
    async def process_async(self, data: np.ndarray) -> np.ndarray:
        """
        Versão assíncrona do processamento completo
        
        Args:
            data: Array com sinais EEG
            
        Returns:
            Array com sinais processados
        """
        try:
            # Remove média em paralelo
            data = await asyncio.to_thread(
                lambda x: x - np.mean(x, axis=1, keepdims=True),
                data
            )
            
            # Aplica filtros
            filtered = await asyncio.to_thread(
                self.apply_filters,
                data
            )
            
            # Remove artefatos
            clean = await asyncio.to_thread(
                self.remove_artifacts,
                filtered
            )
            
            # Aplica CAR
            processed = await asyncio.to_thread(
                self.apply_car,
                clean
            )
            
            return processed
            
        except Exception as e:
            logger.error(f"Erro no processamento assíncrono: {str(e)}")
            raise

    def apply_filters(self, data: np.ndarray) -> np.ndarray:
        """
        Aplica filtros ao sinal
        
        Args:
            data: Array com sinais EEG (channels x samples)
            
        Returns:
            Array com sinais filtrados
        """
        filtered = data.copy()
        
        # Aplica filtro notch
        filtered = signal.filtfilt(
            self.notch_b,
            self.notch_a,
            filtered,
            axis=1
        )
        
        # Aplica filtro passa-banda
        filtered = signal.filtfilt(
            self.bandpass_b,
            self.bandpass_a,
            filtered,
            axis=1
        )
        
        return filtered
    
    def remove_artifacts(self, data: np.ndarray) -> np.ndarray:
        """
        Remove artefatos do sinal
        
        Args:
            data: Array com sinais EEG
            
        Returns:
            Array com sinais limpos
        """
        clean_data = data.copy()
        
        for ch in range(data.shape[0]):
            # Detecta amostras ruins
            bad_samples = np.abs(data[ch]) > self.config.artifact_threshold
            
            if np.any(bad_samples):
                # Identifica segmentos contínuos ruins
                segments = self._find_bad_segments(bad_samples)
                
                # Interpola segmentos ruins
                for start, end in segments:
                    if start > 0 and end < len(data[ch]):
                        # Interpolação linear
                        clean_data[ch, start:end] = np.interp(
                            np.arange(start, end),
                            [start-1, end],
                            [data[ch, start-1], data[ch, end]]
                        )
        
        return clean_data
    
    def apply_car(self, data: np.ndarray) -> np.ndarray:
        """
        Aplica Common Average Reference
        
        Args:
            data: Array com sinais EEG
            
        Returns:
            Array com sinais re-referenciados
        """
        # Calcula média entre todos os canais
        common_avg = np.mean(data, axis=0, keepdims=True)
        
        # Subtrai média de todos os canais
        return data - common_avg
    
    def calculate_artifact_ratio(self, data: np.ndarray) -> float:
        """
        Calcula a proporção de amostras com artefatos
        """
        # Define limiares para diferentes tipos de artefatos
        amplitude_threshold = 100  # microvolts
        variance_threshold = 50
        derivative_threshold = 20

        # Conta amostras com artefatos
        artifacts = 0
        total_samples = data.shape[1]
        
        for ch in range(data.shape[0]):
            # Verifica amplitude excessiva
            amplitude_artifacts = np.sum(np.abs(data[ch]) > amplitude_threshold)
            
            # Verifica variações bruscas (derivada)
            diff = np.diff(data[ch])
            derivative_artifacts = np.sum(np.abs(diff) > derivative_threshold)
            
            # Verifica variância local
            variance = np.var(data[ch])
            if variance > variance_threshold:
                artifacts += 1
                
            artifacts += amplitude_artifacts + derivative_artifacts

        # Calcula razão
        artifact_ratio = min(artifacts / (total_samples * data.shape[0]), 1.0)
        
        return artifact_ratio
    
    def check_signal_quality(self, data: np.ndarray) -> Dict[str, any]:
        """Verifica qualidade do sinal"""
        try:
            quality = {}
            
            # Verifica amplitude
            quality['amplitude_ok'] = np.all(
                np.abs(data) < self.config.artifact_threshold
            )
            
            # Verifica variância (detecta canais mortos)
            channel_vars = np.var(data, axis=1)
            quality['variance_ok'] = np.all(channel_vars > 0.1)
            
            # Verifica linha de base
            baselines = np.mean(data, axis=1)
            quality['baseline_ok'] = np.all(np.abs(baselines) < 10)
            
            # Verifica ruído em 60Hz
            quality['line_noise_ok'] = self._check_line_noise(data)
            
            # Adiciona o cálculo de artifact_ratio
            quality['artifact_ratio'] = self.calculate_artifact_ratio(data)
            
            # Score geral ajustado para incluir artifact_ratio
            quality['overall_score'] = np.mean([
                float(v) for v in quality.values() 
                if isinstance(v, bool)
            ]) * (1 - quality['artifact_ratio'])
            
            return quality
            
        except Exception as e:
            logger.error(f"Erro na verificação de qualidade: {str(e)}")
            return {
                'amplitude_ok': False,
                'variance_ok': False,
                'baseline_ok': False,
                'line_noise_ok': False,
                'artifact_ratio': 1.0,
                'overall_score': 0.0
            }

    async def check_quality_async(self, epoch: np.ndarray) -> Dict[str, bool]:
        """
        Versão assíncrona da checagem de qualidade
        
        Args:
            epoch: Array com época EEG
            
        Returns:
            Dicionário com métricas de qualidade
        """
        return await asyncio.to_thread(self.check_signal_quality, epoch)
    
    async def denoise_async(self, epoch: np.ndarray) -> np.ndarray:
        """
        Versão assíncrona do denoising
        
        Args:
            epoch: Array com época EEG
            
        Returns:
            Array com sinais limpos
        """
        return await asyncio.to_thread(self._wavelet_denoise, epoch)

    def _wavelet_denoise(self, data: np.ndarray) -> np.ndarray:
        """
        Aplica denoising usando wavelets
        
        Args:
            data: Array com sinais EEG
            
        Returns:
            Array com sinais limpos
        """
        denoised = np.zeros_like(data)
        
        for ch in range(data.shape[0]):
            # Decomposição wavelet
            coeffs = pywt.wavedec(data[ch], 'db4', level=4)
            
            # Calcula threshold
            noise_est = self._estimate_noise(coeffs[-1])
            threshold = noise_est * np.sqrt(2 * np.log(len(data[ch])))
            
            # Aplica threshold nos coeficientes de detalhe
            new_coeffs = [coeffs[0]]  # Mantém aproximação
            for detail in coeffs[1:]:
                new_coeffs.append(pywt.threshold(
                    detail,
                    threshold,
                    mode='soft'
                ))
            
            # Reconstrói sinal
            denoised[ch] = pywt.waverec(new_coeffs, 'db4')
            
            # Ajusta tamanho se necessário
            if len(denoised[ch]) > len(data[ch]):
                denoised[ch] = denoised[ch][:len(data[ch])]
        
        return denoised
    
    def _find_bad_segments(self, bad_samples: np.ndarray) -> List[Tuple[int, int]]:
        """Encontra segmentos contínuos de amostras ruins"""
        segments = []
        start = None
        
        for i, bad in enumerate(bad_samples):
            if bad and start is None:
                start = i
            elif not bad and start is not None:
                segments.append((start, i))
                start = None
                
        if start is not None:
            segments.append((start, len(bad_samples)))
            
        return segments
    
    def _check_line_noise(self, data: np.ndarray) -> bool:
        """Verifica presença de ruído de linha"""
        for ch in range(data.shape[0]):
            # Calcula FFT
            fft = np.fft.fft(data[ch])
            freqs = np.fft.fftfreq(len(data[ch]), 1/self.config.sfreq)
                        
            # Encontra componente em 60Hz
            idx_60hz = np.argmin(np.abs(freqs - 60))
            power_60hz = np.abs(fft[idx_60hz])
            
            # Poder total
            total_power = np.sum(np.abs(fft))
            
            # Se poder em 60Hz > 20% do total, considera ruído excessivo
            if power_60hz / total_power > 0.2:
                return False
                
        return True
    
    def _estimate_noise(self, detail_coeffs: np.ndarray) -> float:
        """
        Estima nível de ruído usando coeficientes wavelet
        
        Args:
            detail_coeffs: Coeficientes de detalhe wavelet
            
        Returns:
            Estimativa do nível de ruído
        """
        # Usa MAD (Median Absolute Deviation) para estimativa robusta
        return np.median(np.abs(detail_coeffs - np.median(detail_coeffs))) / 0.6745
    
    async def process(self, data: np.ndarray) -> np.ndarray:
        """Versão síncrona do processamento"""
        try:
            # Remove média
            data = data - np.mean(data, axis=1, keepdims=True)
            
            # Aplica filtros
            filtered = self.apply_filters(data)
            
            # Remove artefatos
            clean = self.remove_artifacts(filtered)
            
            # Aplica CAR
            processed = self.apply_car(clean)
            
            return processed
        except Exception as e:
            logger.error(f"Erro no processamento: {str(e)}")
            raise

    async def get_band_power(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """Calcula poder nas diferentes bandas de frequência de forma assíncrona"""
        try:
            return await asyncio.to_thread(self._calculate_band_power, data)
        except Exception as e:
            logger.error(f"Erro no cálculo de poder: {str(e)}")
            return {band: np.zeros(data.shape[0]) for band in ['delta', 'theta', 'alpha', 'beta', 'gamma']}

    def _calculate_band_power(self, data: np.ndarray) -> Dict[str, float]:
        """Implementação síncrona do cálculo de poder das bandas"""
        # Garante que os dados não são zeros
        if np.all(data == 0):
            logger.warning("Dados de entrada contém apenas zeros")
            return {band: 0.0 for band in ['delta', 'theta', 'alpha', 'beta', 'gamma']}

        # Converte NaN/Inf para números
        data = np.nan_to_num(data)
        
        # Calcula PSD
        nperseg = min(64, data.shape[1])
        freqs, psd = signal.welch(data, fs=self.config.sfreq, nperseg=nperseg)
        
        # Calcula poder médio para cada banda
        powers = {}
        for band, (low, high) in {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 45)
        }.items():
            mask = (freqs >= low) & (freqs <= high)
            if np.any(mask):
                # Média do PSD na banda de frequência
                band_power = np.mean(psd[:, mask])
                # Normaliza e converte para float
                powers[band] = float(np.log1p(band_power))
            else:
                powers[band] = 0.0
                
        # Normaliza para soma = 1
        total = sum(powers.values()) + 1e-10
        powers = {k: v/total for k, v in powers.items()}
        
        return powers

    def _check_line_noise(self, data: np.ndarray) -> bool:
        """Verifica presença de ruído de linha"""
        try:
            total_power = 1e-10  # Valor mínimo para evitar divisão por zero
            
            for ch in range(data.shape[0]):
                fft = np.fft.fft(data[ch])
                freqs = np.fft.fftfreq(len(data[ch]), 1/self.config.sfreq)
                
                # Encontra componente em 60Hz
                idx_60hz = np.argmin(np.abs(freqs - 60))
                power_60hz = np.abs(fft[idx_60hz])
                
                total_power = max(np.sum(np.abs(fft)), total_power)
                
                if power_60hz / total_power > 0.2:
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Erro na verificação de ruído: {str(e)}")
            return False

    async def compute_connectivity(self, data: np.ndarray, method: str = 'plv') -> np.ndarray:
        """
        Calcula conectividade entre canais
        
        Args:
            data: Array com sinais EEG (channels x samples)
            method: Método de conectividade ('plv', 'coherence', ou 'pli')
            
        Returns:
            Matriz de conectividade (channels x channels)
        """
        try:
            n_channels = data.shape[0]
            connectivity = np.zeros((n_channels, n_channels))
            
            for i in range(n_channels):
                for j in range(i+1, n_channels):
                    if method == 'plv':
                        # Phase Locking Value
                        analytic1 = signal.hilbert(data[i])
                        analytic2 = signal.hilbert(data[j])
                        phase_diff = np.angle(analytic1) - np.angle(analytic2)
                        plv = np.abs(np.mean(np.exp(1j * phase_diff)))
                        connectivity[i,j] = plv
                        connectivity[j,i] = plv
                        
                    elif method == 'coherence':
                        # Magnitude Squared Coherence
                        f, Cxy = signal.coherence(data[i], data[j], fs=self.config.sfreq)
                        mask = (f >= 8) & (f <= 13)  # banda alfa
                        coh = np.mean(Cxy[mask])
                        connectivity[i,j] = coh
                        connectivity[j,i] = coh
                        
                    elif method == 'pli':
                        # Phase Lag Index
                        analytic1 = signal.hilbert(data[i])
                        analytic2 = signal.hilbert(data[j])
                        phase_diff = np.angle(analytic1) - np.angle(analytic2)
                        pli = np.abs(np.mean(np.sign(np.sin(phase_diff))))
                        connectivity[i,j] = pli
                        connectivity[j,i] = pli
            
            return connectivity
            
        except Exception as e:
            logger.error(f"Erro no cálculo de conectividade: {str(e)}")
            raise