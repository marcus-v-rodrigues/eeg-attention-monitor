import numpy as np
import time
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import logging
from typing import Dict, List, Tuple, Optional, Any
import asyncio
from dataclasses import dataclass
from .signal_processor import EEGProcessor, SignalConfig
from .feature_extractor import EEGFeatureExtractor

logger = logging.getLogger(__name__)

@dataclass
class BCIConfig:
    """Configurações para o sistema BCI"""
    sfreq: float = 128.0
    window_size: int = 128  # 1 segundo
    overlap: float = 0.5
    channels: List[str] = None
    model_params: Dict = None
    
    def __post_init__(self):
        if self.channels is None:
            self.channels = [
                'AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1',
                'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4'
            ]
        if self.model_params is None:
            self.model_params = {
                'n_estimators': 100,
                'learning_rate': 0.1,
                'max_depth': 3,
                'random_state': 42
            }

class AttentionBCI:
    """Sistema BCI para detecção de estados de atenção"""
    
    def __init__(self, config: Optional[BCIConfig] = None):
        """
        Inicializa o sistema BCI
        
        Args:
            config: Configurações do sistema
        """
        self.config = config or BCIConfig()
        # Inicializa processador
        signal_config = SignalConfig(
            sfreq=self.config.sfreq,
            window_size=self.config.window_size,
            overlap=self.config.overlap
        )
        self.processor = EEGProcessor(signal_config)
        self.signal_processor = EEGProcessor(SignalConfig(sfreq=self.config.sfreq))
        self.feature_extractor = EEGFeatureExtractor(self.config.sfreq)
        
        # Inicializa classificador
        self.classifier = GradientBoostingClassifier(**self.config.model_params)
        self.scaler = StandardScaler()
        
        # Estado do sistema
        self.is_trained = False
        self.training_stats = {}
        
    async def process_epoch(self, epoch: np.ndarray) -> Dict[str, Any]:
        try:
            processed_data = await self.processor.process_async(epoch)
            quality = await self.processor.check_quality_async(processed_data)
            
            if not quality['amplitude_ok']:
                processed_data = await self.processor.denoise_async(processed_data)
            
            # Usa get_band_power em vez de compute_band_power
            powers = await self.processor.get_band_power(processed_data)
            
            # Converte valores numpy para float
            band_powers = {
                band: float(power) if np.isscalar(power) else float(power[0])
                for band, power in powers.items()
            }
            
            # Matriz de conectividade
            connectivity = await self.processor.compute_connectivity(processed_data, method='plv')
            
            # Extrai características e métricas
            features = await self.feature_extractor.extract_async(processed_data)
            attention_metrics = await self.feature_extractor.compute_attention_metrics_async(features)

            return {
                'timestamp': time.time(),
                'attention_metrics': attention_metrics,
                'band_powers': band_powers,
                'connectivity': connectivity.tolist(),
                'quality': quality
            }
        except Exception as e:
            logger.error(f"Erro no processamento: {str(e)}")
            raise
    
    async def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        Treina o sistema BCI
        
        Args:
            X: Dados de treino (epochs x channels x samples)
            y: Rótulos (0: baixa atenção, 1: alta atenção)
            
        Returns:
            Dicionário com métricas de treino
        """
        try:
            # Processa todas as épocas
            processed_epochs = []
            for epoch in X:
                processed = await self.signal_processor.process_async(epoch)
                processed_epochs.append(processed)
            
            # Extrai características
            features_list = []
            for processed in processed_epochs:
                features = await self.feature_extractor.extract_async(processed)
                features_list.append(self._prepare_features(features))
            
            # Prepara dados para treino
            X_features = np.vstack(features_list)
            X_scaled = self.scaler.fit_transform(X_features)
            
            # Treina classificador
            self.classifier.fit(X_scaled, y)
            self.is_trained = True
            
            # Calcula métricas
            train_score = self.classifier.score(X_scaled, y)
            feature_importance = dict(zip(
                self.feature_extractor.feature_names,
                self.classifier.feature_importances_
            ))
            
            self.training_stats = {
                'train_score': train_score,
                'feature_importance': feature_importance,
                'n_epochs': len(X),
                'n_features': X_scaled.shape[1]
            }
            
            return self.training_stats
            
        except Exception as e:
            logger.error(f"Erro no treinamento: {str(e)}")
            raise
    
    async def predict(self, epoch: np.ndarray) -> Dict[str, Any]:
        """
        Realiza predição para uma época
        
        Args:
            epoch: Array com dados EEG
            
        Returns:
            Dicionário com predições e métricas
        """
        if not self.is_trained:
            raise RuntimeError("Modelo não treinado")
        
        try:
            # Processa época
            result = await self.process_epoch(epoch)
            
            # Prepara características
            features = self._prepare_features(result['features'])
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Realiza predição
            probs = self.classifier.predict_proba(features_scaled)
            pred = self.classifier.predict(features_scaled)
            
            result.update({
                'prediction': int(pred[0]),
                'probability': float(probs[0, 1]),
                'confidence': float(max(probs[0]))
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na predição: {str(e)}")
            raise
    
    def _prepare_features(self, features: Dict) -> np.ndarray:
        """Prepara características para classificação"""
        return np.array([
            features[name] for name in self.feature_extractor.feature_names
        ])

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo"""
        return {
            'is_trained': self.is_trained,
            'training_stats': self.training_stats,
            'config': {
                'sfreq': self.config.sfreq,
                'window_size': self.config.window_size,
                'channels': self.config.channels,
                'model_params': self.config.model_params
            }
        }