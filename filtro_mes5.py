import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

def carregar_arquivo_sisfall(caminho_arquivo):
    # Alterna automaticamente entre .txt e .csv caso um deles não exista no caminho informado
    if not os.path.exists(caminho_arquivo):
        base, ext = os.path.splitext(caminho_arquivo)
        alternativo = base + ('.csv' if ext.lower() == '.txt' else '.txt')
        if os.path.exists(alternativo):
            caminho_arquivo = alternativo
        else:
            raise FileNotFoundError(f"Arquivo não encontrado (.txt ou .csv): {caminho_arquivo}")

    nomes_colunas = ['ADXL_X', 'ADXL_Y', 'ADXL_Z', 'ITG_X', 'ITG_Y', 'ITG_Z', 'MMA_X', 'MMA_Y', 'MMA_Z']

    if caminho_arquivo.lower().endswith('.csv'):
        df_raw = pd.read_csv(caminho_arquivo)
        if 'ADXL345_Acc_X' in df_raw.columns:
            df = pd.DataFrame()
            # Os arquivos .csv pré-processados já estão em unidades de gravidade (g)
            df['Eixo_X_g'] = pd.to_numeric(df_raw['ADXL345_Acc_X'], errors='coerce')
            df['Eixo_Y_g'] = pd.to_numeric(df_raw['ADXL345_Acc_Y'], errors='coerce')
            df['Eixo_Z_g'] = pd.to_numeric(df_raw['ADXL345_Acc_Z'], errors='coerce')
            return df.dropna(), caminho_arquivo
        else:
            df = pd.read_csv(caminho_arquivo, sep=',', names=nomes_colunas, usecols=range(9))
    else:
        df = pd.read_csv(caminho_arquivo, sep=',', names=nomes_colunas, usecols=range(9), engine='c')

    for col in ['ADXL_X', 'ADXL_Y', 'ADXL_Z']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['ADXL_X', 'ADXL_Y', 'ADXL_Z'])

    df['Eixo_X_g'] = df['ADXL_X'] / 256.0
    df['Eixo_Y_g'] = df['ADXL_Y'] / 256.0
    df['Eixo_Z_g'] = df['ADXL_Z'] / 256.0
    return df, caminho_arquivo

caminho_arquivo = 'SisFall_dataset/SE01/D01_SE01_R01.txt'
df, caminho_real = carregar_arquivo_sisfall(caminho_arquivo)

frequencia_amostragem = 200.0 # Sensor gravou a 200 Hz
frequencia_corte = 5.0 # Cortar tudo acima de 5 Hz (Movimento Humano)
ordem = 4 # Filtro de 4ª ordem

# Teorema de Nyquist
frequencia_nyquist = 0.5 * frequencia_amostragem
corte_normalizado = frequencia_corte / frequencia_nyquist

b, a = butter(ordem, corte_normalizado, btype='low', analog=False)

df['X_filtrado'] = filtfilt(b, a, df['Eixo_X_g'])
df['Y_filtrado'] = filtfilt(b, a, df['Eixo_Y_g'])
df['Z_filtrado'] = filtfilt(b, a, df['Eixo_Z_g'])

# Um Bruto e um Filtrado para comparação
df['SVM_Bruto'] = np.sqrt(df['Eixo_X_g']**2 + df['Eixo_Y_g']**2 + df['Eixo_Z_g']**2)
df['SVM_Filtrado'] = np.sqrt(df['X_filtrado']**2 + df['Y_filtrado']**2 + df['Z_filtrado']**2)

tempo_segundos = np.arange(len(df)) / frequencia_amostragem

plt.figure(figsize=(12, 6))

# Linha do sinal sujo (ruído original)
plt.plot(tempo_segundos, df['SVM_Bruto'], color='lightcoral', alpha=0.6, label='SVM Bruto (Com Ruído)', linewidth=1)

# Linha do sinal limpo pelo Butterworth
plt.plot(tempo_segundos, df['SVM_Filtrado'], color='darkred', label='SVM Filtrado (Butterworth 5Hz)', linewidth=2)

plt.axhline(y=1.0, color='gray', linestyle=':', label='Gravidade Basal (1.0g)')
plt.title('Filtragem Digital de Sinal Inercial - Caminhada (SisFall - D01_SE01)', fontsize=14)
plt.xlabel('Tempo (segundos)', fontsize=12)
plt.ylabel('Magnitude Resultante (g)', fontsize=12)

# Zoom nos primeiros 10 segundos para visualização do ganho de suavidade
plt.xlim(0, 10)
plt.ylim(0, 3)

plt.legend(loc='upper right')
plt.grid(True)
plt.tight_layout()
plt.savefig('comparativo_butterworth_M5.png', dpi=300)
print("Sinal processado e imagem 'comparativo_butterworth_M5.png' gerada.")
