import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from scipy import signal

@dataclass
class AttentionMetrics:
    mean_attention: float  # Média da atenção
    attention_variance: float  # Variância da atenção
    engagement_index: float  # Índice de engajamento
    attention_trend: str  # 'aumentando', 'estável', 'diminuindo'
    dominant_frequency: float  # Frequência dominante
    alpha_beta_ratio: float  # Razão alfa/beta
    theta_beta_ratio: float  # Razão teta/beta
    meditation_score: float  # Pontuação de meditação
    
class EEGAnalyzer:
    def __init__(self, sampling_rate: float = 128.0):
        """
        Inicializa o analisador EEG
        
        Args:
            sampling_rate: Taxa de amostragem em Hz
        """
        self.sampling_rate = sampling_rate
        self.previous_attention = 0.5  # Inicializa com valor médio
        self.frequency_bands = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 45)
        }
    
    def analyze_attention(self, eeg_data: np.ndarray, window_size: int = 128) -> AttentionMetrics:
        """
        Analisa dados EEG para extrair métricas de atenção
        
        Args:
            eeg_data: Array de forma (canais, amostras)
            window_size: Tamanho da janela de análise
            
        Returns:
            Objeto AttentionMetrics com as métricas calculadas
        """
        if len(eeg_data.shape) != 2:
            raise ValueError("Dados EEG devem ser array 2D (canais x amostras)")
            
        # Calcula poder nas bandas
        band_powers = self._compute_band_powers(eeg_data)
        
        # Calcula métricas
        alpha_beta = band_powers['alpha'] / (band_powers['beta'] + 1e-10)
        theta_beta = band_powers['theta'] / (band_powers['beta'] + 1e-10)
        
        # Pontuação de atenção baseada no inverso da razão teta/beta
        attention = 1 / (1 + theta_beta)
        
        # Índice de engajamento: beta / (alfa + teta)
        engagement = band_powers['beta'] / (band_powers['alpha'] + band_powers['theta'] + 1e-10)
        
        # Calcula pontuação de meditação baseada no poder alfa
        meditation = self._calculate_meditation_score(band_powers)
        
        # Calcula tendência da atenção
        trend = self._calculate_trend(attention)
        
        # Encontra frequência dominante
        freqs, psd = signal.welch(np.mean(eeg_data, axis=0), fs=self.sampling_rate)
        dominant_freq = freqs[np.argmax(psd)]
        
        # Calcula variância da atenção usando janelas sobrepostas
        attention_var = self._calculate_attention_variance(eeg_data, window_size)
        
        return AttentionMetrics(
            mean_attention=float(attention),
            attention_variance=float(attention_var),
            engagement_index=float(engagement),
            attention_trend=trend,
            dominant_frequency=float(dominant_freq),
            alpha_beta_ratio=float(alpha_beta),
            theta_beta_ratio=float(theta_beta),
            meditation_score=float(meditation)
        )
    
    def _compute_band_powers(self, eeg_data: np.ndarray) -> Dict[str, float]:
        """Calcula o poder em diferentes bandas de frequência"""
        nperseg = min(128, eeg_data.shape[1])
        freqs, psd = signal.welch(np.mean(eeg_data, axis=0), fs=self.sampling_rate, nperseg=nperseg)
        
        powers = {}
        for band, (low, high) in self.frequency_bands.items():
            mask = (freqs >= low) & (freqs <= high)
            powers[band] = np.mean(psd[mask]) if np.any(mask) else 0.0
            
        return powers
    
    def _calculate_meditation_score(self, band_powers: Dict[str, float]) -> float:
        """Calcula pontuação de meditação baseada no poder alfa e razão alfa/teta"""
        alpha_power = band_powers['alpha']
        theta_power = band_powers['theta']
        
        # Normaliza poder alfa
        max_alpha = 100  # Poder alfa máximo típico
        norm_alpha = min(alpha_power / max_alpha, 1.0)
        
        # Calcula contribuição da razão alfa/teta
        alpha_theta_ratio = alpha_power / (theta_power + 1e-10)
        ratio_score = 1 / (1 + np.exp(-alpha_theta_ratio + 2))
        
        # Combina métricas
        meditation_score = 0.6 * norm_alpha + 0.4 * ratio_score
        return float(meditation_score)
    
    def _calculate_trend(self, current_attention: float, threshold: float = 0.1) -> str:
        """Determina tendência da atenção"""
        if current_attention > 0.7 and current_attention - self.previous_attention > threshold:
            trend = 'aumentando'
        elif current_attention < 0.3 and self.previous_attention - current_attention > threshold:
            trend = 'diminuindo'
        else:
            trend = 'estável'
            
        self.previous_attention = current_attention
        return trend
    
    def _calculate_attention_variance(self, eeg_data: np.ndarray, window_size: int) -> float:
        """Calcula variância da atenção usando janelas sobrepostas"""
        n_samples = eeg_data.shape[1]
        attention_scores = []
        
        for i in range(0, n_samples - window_size + 1, window_size // 2):
            window = eeg_data[:, i:i+window_size]
            powers = self._compute_band_powers(window)
            theta_beta = powers['theta'] / (powers['beta'] + 1e-10)
            attention = 1 / (1 + theta_beta)
            attention_scores.append(attention)
            
        return np.var(attention_scores) if attention_scores else 0.0

# Exemplo de uso
if __name__ == "__main__":
    from src.data_loader import EEGDataLoader
    
    # Carrega dados usando o loader existente
    loader = EEGDataLoader()
    sample = loader.get_next_sample()
    
    # Converte dados do formato do loader para numpy array
    channels_data = []
    for channel in loader.channels:
        channels_data.append(sample['channels'][channel])
    sample_data = np.array(channels_data)
    
    # Cria analisador e processa dados
    
    # Cria analisador e processa dados
    analyzer = EEGAnalyzer(sampling_rate=128.0)
    metrics = analyzer.analyze_attention(sample_data)
    
    print(f"Atenção Média: {metrics.mean_attention:.2f}")
    print(f"Variância da Atenção: {metrics.attention_variance:.2f}")
    print(f"Índice de Engajamento: {metrics.engagement_index:.2f}")
    print(f"Tendência da Atenção: {metrics.attention_trend}")
    print(f"Pontuação de Meditação: {metrics.meditation_score:.2f}")