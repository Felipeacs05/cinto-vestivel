import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

caminho_arquivo = 'SisFall_dataset/SE01/D01_SE01_R01.txt'
nomes_colunas = ['ADXL_X', 'ADXL_Y', 'ADXL_Z', 'ITG_X', 'ITG_Y', 'ITG_Z', 'MMA_X', 'MMA_Y', 'MMA_Z']
df = pd.read_csv(caminho_arquivo, sep=',', names=nomes_colunas, engine='python')
df['MMA_Z'] = df['MMA_Z'].astype(str).str.replace(';', '').astype(float)

df['Eixo_X_g'] = df['ADXL_X'] / 256.0
df['Eixo_Y_g'] = df['ADXL_Y'] / 256.0
df['Eixo_Z_g'] = df['ADXL_Z'] / 256.0

frequencia_amostragem = 200.0 # Sensor gravou a 200 Hz
frequencia_corte = 5.0 # Cortar tudo acima de 5 Hz (Movimento Humano)
ordem = 4 # Filtro de 4ª ordem

#Teorema de Nyquist
frequencia_nyquist = 0.5 * frequencia_amostragem
corte_normalizado = frequencia_corte / frequencia_nyquist

b, a = butter(ordem, corte_normalizado, btype='low', analog=False)