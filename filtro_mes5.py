import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

caminho_arquivo = 'SisFall_dataset/SE01/D01_SE01_R01.txt'
nomes_colunas = ['ADXL_X', 'ADXL_Y', 'ADXL_Z', 'ITG_X', 'ITG_Y', 'ITG_Z', 'MMA_X', 'MMA_Y', 'MMA_Z']
df = pd.read_csv(caminho_arquivo, sep=',', names=nomes_colunas, engine='python')
df['MMA_Z'] = df['MMA_Z'].astype(str).str.replace(';', '').astype(float)