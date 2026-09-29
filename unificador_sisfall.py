import os
import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
import warnings

# Ignorar pequenos avisos de formatação do pandas durante a leitura massiva
warnings.filterwarnings('ignore')

print("Iniciando o Pipeline de Unificação e Filtragem do SisFall...")
print("Isso pode levar alguns minutos. Por favor, aguarde...\n")

# 1. CONFIGURAÇÕES DO FILTRO BUTTERWORTH (5 Hz, 4ª Ordem)
frequencia_amostragem = 200.0
frequencia_corte = 5.0
ordem_filtro = 4
corte_normalizado = frequencia_corte / (0.5 * frequencia_amostragem)
b, a = butter(ordem_filtro, corte_normalizado, btype='low', analog=False)