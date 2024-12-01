import numpy as np
from scipy import signal, stats
import pywt
import logging
from typing import Dict, List, Optional, Any
import asyncio

logger = logging.getLogger(__name__)

class EEGFeatureExtractor:
    """Extrator de características para sinais EEG"""
    
    def __init__(self, sfreq: float = 128.0):
        """
        Inicializa o extrator
        
        Args:
            sfreq: Frequência de amostragem
        """
        self.sfreq = sfreq
        self.feature_names = []
        self._initialize_feature_names()
    
    def _initialize_feature_names(self):
        """Inicializa nomes das características"""
        # Características temporais
        temporal = ['mean', 'std', 'kurtosis', 'skewness', 'mobility', 'complexity']
        
        # Características espectrais
        bands = ['delta', 'theta', 'alpha', 'beta', 'gamma']
        spectral = [f"{band}_{metric}" for band in bands 
                   for metric in ['power', 'rel_power', 'peak_freq']]
        
        # Características de conectividade
        connectivity = ['coherence', 'plv', 'pli']
        
        # Características não-lineares
        nonlinear = ['sample_entropy', 'hurst_exponent', 'dfa']
        
        self.feature_names = temporal + spectral + connectivity + nonlinear
    
    async def extract_async(self, epoch: np.ndarray) -> Dict[str, float]:
        """
        Extrai características de forma assíncrona
        
        Args:
            epoch: Época EEG (channels x samples)
            
        Returns:
            Dicionário com características
        """
        try:
            # Executa extrações em paralelo
            temporal = asyncio.create_task(
                self._extract_temporal_features_async(epoch)
            )
            spectral = asyncio.create_task(
                self._extract_spectral_features_async(epoch)
            )
            connectivity = asyncio.create_task(
                self._extract_connectivity_features_async(epoch)
            )
            nonlinear = asyncio.create_task(
                self._extract_nonlinear_features_async(epoch)
            )
            
            # Aguarda resultados
            results = await asyncio.gather(
                temporal, spectral, connectivity, nonlinear
            )
            
            # Combina resultados
            features = {}
            for result in results:
                features.update(result)
            
            return features
            
        except Exception as e:
            logger.error(f"Erro na extração de características: {str(e)}")
            raise
    
    def _compute_spectral_features(self, epoch: np.ndarray) -> Dict[str, float]:
        """Calcula características espectrais"""
        features = {}
        
        for ch in range(epoch.shape[0]):
            # Ajusta tamanho da janela
            nperseg = min(64, epoch.shape[1])
            freqs, psd = signal.welch(epoch[ch], fs=self.sfreq, nperseg=nperseg)
            
            # Evita divisão por zero
            total_power = max(np.sum(psd), 1e-10)
            
            # Poder nas bandas
            for band_name, (fmin, fmax) in [
                ('delta', (0.5, 4)),
                ('theta', (4, 8)),
                ('alpha', (8, 13)),
                ('beta', (13, 30)),
                ('gamma', (30, 45))
            ]:
                mask = (freqs >= fmin) & (freqs <= fmax)
                if np.any(mask):
                    power = np.mean(psd[mask])
                    rel_power = power / total_power
                    peak_freq = freqs[mask][np.argmax(psd[mask])] if len(psd[mask]) > 0 else 0
                else:
                    power = 0
                    rel_power = 0
                    peak_freq = 0
                
                prefix = f'ch{ch}_{band_name}_'
                features.update({
                    prefix + 'power': float(power),
                    prefix + 'rel_power': float(rel_power),
                    prefix + 'peak_freq': float(peak_freq)
                })
        
        return features

    def _sample_entropy(self, signal: np.ndarray, m: int = 2, r: float = 0.2) -> float:
        """Calcula entropia da amostra"""
        if len(signal) == 0 or np.std(signal) == 0:
            return 0.0
            
        # Normaliza o sinal
        signal = signal - np.mean(signal)
        std = np.std(signal)
        if std > 0:
            signal = signal / std
        r = r * (std if std > 0 else 1)
        
        def _count_matches(template, m):
            if len(template) < m:
                return 0
            n = len(signal) - m + 1
            count = 0
            for i in range(n):
                match = True
                for j in range(m):
                    if i+j >= len(signal) or abs(signal[i+j] - template[j]) > r:
                        match = False
                        break
                if match:
                    count += 1
            return max(0, count - 1)  # Remove self-match
        
        # Calcula para m e m+1
        A = sum(_count_matches(signal[i:i+m], m) 
                for i in range(len(signal)-m+1))
        B = sum(_count_matches(signal[i:i+m+1], m+1) 
                for i in range(len(signal)-m))
        
        # Retorna entropia da amostra
        return -np.log(max(B, 1e-10) / max(A, 1e-10)) if A > 0 else 0

    def _detrended_fluctuation_analysis(self, signal: np.ndarray) -> float:
        """Calcula DFA (Detrended Fluctuation Analysis)"""
        try:
            # Remove tendência
            signal = signal - np.mean(signal)
            
            # Integra o sinal
            y = np.cumsum(signal)
            
            # Escalas para análise
            scales = np.logspace(1, np.log10(len(signal)//4), 20).astype(int)
            scales = scales[scales > 1]  # Remove escalas muito pequenas
            
            if len(scales) == 0:
                return 0.0
                
            fluct = []
            for scale in scales:
                n_segments = len(signal) // scale
                fluctuations = []
                
                for i in range(n_segments):
                    segment = y[i*scale:(i+1)*scale]
                    x = np.arange(len(segment))
                    coef = np.polyfit(x, segment, 1)
                    trend = np.polyval(coef, x)
                    rms = np.sqrt(np.mean((segment - trend)**2))
                    fluctuations.append(rms)
                
                if fluctuations:
                    fluct.append(np.mean(fluctuations))
                
            if not fluct or not all(f > 0 for f in fluct):
                return 0.0
                
            # Calcula expoente alpha
            scales_log = np.log10(scales)
            fluct_log = np.log10(fluct)
            alpha = np.polyfit(scales_log, fluct_log, 1)[0]
            
            return float(alpha)
            
        except Exception as e:
            logger.error(f"Erro no DFA: {str(e)}")
            return 0.0
    
    async def _extract_temporal_features_async(
        self, 
        epoch: np.ndarray
    ) -> Dict[str, float]:
        """Extrai características temporais de forma assíncrona"""
        return await asyncio.to_thread(self._compute_temporal_features, epoch)
    
    async def _extract_spectral_features_async(
        self, 
        epoch: np.ndarray
    ) -> Dict[str, float]:
        """Extrai características espectrais de forma assíncrona"""
        return await asyncio.to_thread(self._compute_spectral_features, epoch)
    
    async def _extract_connectivity_features_async(
        self, 
        epoch: np.ndarray
    ) -> Dict[str, float]:
        """Extrai características de conectividade de forma assíncrona"""
        return await asyncio.to_thread(self._compute_connectivity_features, epoch)
    
    async def _extract_nonlinear_features_async(
        self, 
        epoch: np.ndarray
    ) -> Dict[str, float]:
        """Extrai características não-lineares de forma assíncrona"""
        return await asyncio.to_thread(self._compute_nonlinear_features, epoch)
    
    def _compute_temporal_features(self, epoch: np.ndarray) -> Dict[str, float]:
        """Calcula características temporais"""
        features = {}
        
        for ch in range(epoch.shape[0]):
            prefix = f'ch{ch}_'
            features.update({
                prefix + 'mean': np.mean(epoch[ch]),
                prefix + 'std': np.std(epoch[ch]),
                prefix + 'kurtosis': stats.kurtosis(epoch[ch]),
                prefix + 'skewness': stats.skew(epoch[ch]),
                prefix + 'mobility': self._hjorth_mobility(epoch[ch]),
                prefix + 'complexity': self._hjorth_complexity(epoch[ch])
            })
        
        return features
    
    def _compute_connectivity_features(self, epoch: np.ndarray) -> Dict[str, float]:
        """Calcula características de conectividade"""
        features = {}
        n_channels = epoch.shape[0]
        # Coerência entre pares de canais
        
        for i in range(n_channels):
            for j in range(i+1, n_channels):
                # Calcula coerência
                f, coh = signal.coherence(epoch[i], epoch[j], fs=self.sfreq)
                
                # Média nas bandas de interesse
                for band_name, (fmin, fmax) in [
                    ('alpha', (8, 13)),
                    ('beta', (13, 30))
                ]:
                    mask = (f >= fmin) & (f <= fmax)
                    mean_coh = np.mean(coh[mask])
                    features[f'coherence_{band_name}_ch{i}{j}'] = mean_coh
                
                # Phase Locking Value (PLV)
                plv = self._compute_plv(epoch[i], epoch[j])
                features[f'plv_ch{i}{j}'] = plv
                
                # Phase Lag Index (PLI)
                pli = self._compute_pli(epoch[i], epoch[j])
                features[f'pli_ch{i}{j}'] = pli
        
        return features
    
    def _compute_nonlinear_features(self, epoch: np.ndarray) -> Dict[str, float]:
        """Calcula características não-lineares"""
        features = {}
        
        for ch in range(epoch.shape[0]):
            signal = epoch[ch]
            prefix = f'ch{ch}_'
            
            # Sample Entropy
            features[prefix + 'sample_entropy'] = self._sample_entropy(signal)
            
            # Hurst Exponent
            features[prefix + 'hurst_exponent'] = self._hurst_exponent(signal)
            
            # Detrended Fluctuation Analysis
            features[prefix + 'dfa'] = self._detrended_fluctuation_analysis(signal)
            
            # Características Wavelet
            wavelet_features = self._wavelet_features(signal)
            features.update({
                prefix + k: v for k, v in wavelet_features.items()
            })
        
        return features
    
    def _hjorth_mobility(self, signal: np.ndarray) -> float:
        """Calcula mobilidade de Hjorth"""
        diff = np.diff(signal)
        var_signal = np.var(signal)
        var_diff = np.var(diff)
        
        if var_signal == 0:
            return 0
            
        return np.sqrt(var_diff / var_signal)
    
    def _hjorth_complexity(self, signal: np.ndarray) -> float:
        """Calcula complexidade de Hjorth"""
        diff1 = np.diff(signal)
        diff2 = np.diff(diff1)
        
        var_signal = np.var(signal)
        var_diff1 = np.var(diff1)
        var_diff2 = np.var(diff2)
        
        if var_diff1 == 0:
            return 0
            
        return np.sqrt(var_diff2 * var_signal) / var_diff1
    
    def _sample_entropy(self, signal: np.ndarray, m: int = 2, r: float = 0.2) -> float:
        """
        Calcula entropia da amostra
        
        Args:
            signal: Sinal de entrada
            m: Dimensão de embedding
            r: Tolerância
        """
        # Normaliza o sinal
        signal = (signal - np.mean(signal)) / np.std(signal)
        r = r * np.std(signal)
        
        def _count_matches(template, m):
            """Conta matches para um template"""
            n = len(signal) - m + 1
            count = 0
            
            for i in range(n):
                match = True
                for j in range(m):
                    diff = abs(signal[i+j] - template[j])
                    if diff > r:
                        match = False
                        break
                if match:
                    count += 1
            
            return count - 1  # Remove self-match
        
        # Calcula para m e m+1
        n = len(signal)
        
        A = sum(_count_matches(signal[i:i+m], m) 
                for i in range(n-m+1))
        
        B = sum(_count_matches(signal[i:i+m+1], m+1) 
                for i in range(n-m))
        
        # Retorna entropia da amostra
        if A == 0 or B == 0:
            return 0
        
        return -np.log(B/A)
    
    def _hurst_exponent(self, signal: np.ndarray) -> float:
        """Calcula expoente de Hurst"""
        n = len(signal)
        max_k = int(np.floor(np.log2(n)))
        R_S_dict = []
        
        for k in range(2, max_k+1):
            R_S = []
            n_samples = 2**k
            
            # Divide o sinal em segmentos
            n_segments = int(np.floor(n/n_samples))
            
            for i in range(n_segments):
                start = i * n_samples
                segment = signal[start:start+n_samples]
                
                # Remove tendência
                x = np.arange(n_samples)
                coef = np.polyfit(x, segment, 1)
                trend = np.polyval(coef, x)
                segment = segment - trend
                
                # Calcula R/S
                Z = np.cumsum(segment - np.mean(segment))
                R = np.max(Z) - np.min(Z)
                S = np.std(segment)
                
                if S > 0:
                    R_S.append(R/S)
            
            if R_S:
                R_S_dict.append((np.log2(n_samples), np.log2(np.mean(R_S))))
        
        # Calcula expoente através de regressão linear
        if len(R_S_dict) > 1:
            x = np.array([x[0] for x in R_S_dict])
            y = np.array([x[1] for x in R_S_dict])
            H = np.polyfit(x, y, 1)[0]
            return H
        
        return 0.5
    
    def _wavelet_features(self, signal: np.ndarray) -> Dict[str, float]:
        wavelet = 'db4'
        # Calcula level máximo baseado no tamanho do sinal
        max_level = pywt.dwt_max_level(len(signal), pywt.Wavelet(wavelet).dec_len)
        level = min(5, max_level)  # Usa o menor entre 5 e max_level
        features = {}
        
        coeffs = pywt.wavedec(signal, wavelet, level=level)
        
        # Análise dos coeficientes
        for i, coef in enumerate(coeffs):
            prefix = f'wavelet_level{i}_'
            
            # Energia
            energy = np.sum(coef**2)
            
            # Entropia
            if energy > 0:
                coef_norm = coef**2 / energy
                entropy = -np.sum(coef_norm * np.log2(coef_norm + 1e-10))
            else:
                entropy = 0
            
            features.update({
                prefix + 'energy': energy,
                prefix + 'entropy': entropy,
                prefix + 'max': np.max(np.abs(coef)),
                prefix + 'mean': np.mean(np.abs(coef)),
                prefix + 'std': np.std(coef)
            })
        
        return features
    
    def _compute_plv(self, signal1: np.ndarray, signal2: np.ndarray) -> float:
        """Calcula Phase Locking Value"""
        # Transforma de Hilbert
        analytic1 = signal.hilbert(signal1)
        analytic2 = signal.hilbert(signal2)
        
        # Diferença de fase
        phase_diff = np.angle(analytic1) - np.angle(analytic2)
        
        # PLV
        plv = np.abs(np.mean(np.exp(1j * phase_diff)))
        
        return plv
    
    def _compute_pli(self, signal1: np.ndarray, signal2: np.ndarray) -> float:
        """Calcula Phase Lag Index"""
        # Transforma de Hilbert
        analytic1 = signal.hilbert(signal1)
        analytic2 = signal.hilbert(signal2)
        
        # Diferença de fase
        phase_diff = np.angle(analytic1) - np.angle(analytic2)
        
        # PLI
        pli = np.abs(np.mean(np.sign(np.sin(phase_diff))))
        
        return pli
    
    async def compute_attention_metrics_async(
        self, 
        features: Dict[str, float]
    ) -> Dict[str, float]:
        """Calcula métricas de atenção"""
        try:
            # Extrai poderes das bandas dos canais frontais
            ch_powers = {
                'theta': np.mean([v for k, v in features.items() if 'theta_power' in k]),
                'alpha': np.mean([v for k, v in features.items() if 'alpha_power' in k]),
                'beta': np.mean([v for k, v in features.items() if 'beta_power' in k])
            }
            
            # Razão theta/beta
            theta_beta = ch_powers['theta'] / (ch_powers['beta'] + 1e-10)
            
            # Índice de engajamento: beta / (alpha + theta)
            engagement = ch_powers['beta'] / (ch_powers['alpha'] + ch_powers['theta'] + 1e-10)
            
            # Normaliza os índices
            theta_beta_norm = np.clip(1 - (theta_beta / 2), 0, 1)  # Inverso da razão
            engagement_norm = np.clip(engagement, 0, 1)
            
            # Score de atenção combinado
            attention_score = 0.6 * theta_beta_norm + 0.4 * engagement_norm
            
            # Estado dos olhos baseado em alfa
            alpha_ratio = ch_powers['alpha'] / (ch_powers['theta'] + ch_powers['beta'] + 1e-10)
            eye_state = 'closed' if alpha_ratio > 0.4 else 'open'
            
            return {
                'attention_score': float(attention_score),
                'engagement_index': float(engagement_norm),
                'theta_beta_ratio': float(theta_beta),
                'eye_state': eye_state
            }
                
        except Exception as e:
            logger.error(f"Erro no cálculo de métricas: {str(e)}")
            return {
                'attention_score': 0.0,
                'engagement_index': 0.0,
                'theta_beta_ratio': 0.0,
                'eye_state': 'open'
            }