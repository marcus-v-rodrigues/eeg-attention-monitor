import numpy as np
import pandas as pd
from collections import deque
from typing import Dict, List

class EEGDataLoader:
    def __init__(self, buffer_size: int = 1000):
        self.data = pd.read_csv('data/eeg-eye-state.csv')
        self.current_index = 0
        self.buffer_size = buffer_size
        self.data_buffer = deque(maxlen=buffer_size)
        self.channels = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1',
                        'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
        
    def get_next_sample(self, window_size: int = 128) -> Dict:
        """Retorna a próxima janela de amostras"""
        if self.current_index + window_size > len(self.data):
            self.current_index = 0
            
        sample_data = self.data.iloc[self.current_index:self.current_index + window_size]
        self.current_index += window_size
        
        # Organiza os dados por canal
        channels_data = {}
        for i, channel in enumerate(self.channels):
            channels_data[channel] = sample_data.iloc[:, i].tolist()
            
        sample = {
            'timestamp': pd.Timestamp.now().timestamp(),
            'channels': channels_data
        }
        
        self.data_buffer.append(sample)
        return sample