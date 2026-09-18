import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Caminho do arquivo a ser analisado
caminho_arquivo = 'SisFall_dataset/SE01/D01_SE01_R01.txt'

nomes_colunas = ['ADXL_X', 'ADXL_Y', 'ADXL_Z', 'ITG_X', 'ITG_Y', 'ITG_Z', 'MMA_X', 'MMA_Y', 'MMA_Z']
df = pd.read_csv(caminho_arquivo, sep=',', names=nomes_colunas, engine='python')
df['MMA_Z'] = df['MMA_Z'].astype(str).str.replace(';', '').astype(float)

# Conversão ADC -> g (ADXL345: 256 LSB/g)
df['Eixo_X_g'] = df['ADXL_X'] / 256.0
df['Eixo_Y_g'] = df['ADXL_Y'] / 256.0
df['Eixo_Z_g'] = df['ADXL_Z'] / 256.0
df['SVM'] = np.sqrt(df['Eixo_X_g']**2 + df['Eixo_Y_g']**2 + df['Eixo_Z_g']**2)

tempo_segundos = np.arange(len(df)) / 200.0
tipo_movimento = "Queda" if "F" in caminho_arquivo else "Atividade Diária"

# Criando 2 subplots verticais para desacoplar as linhas
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Subplot 1: Componentes Triaxiais
ax1.plot(tempo_segundos, df['Eixo_X_g'], color='blue', alpha=0.6, label='Eixo X')
ax1.plot(tempo_segundos, df['Eixo_Y_g'], color='green', alpha=0.6, label='Eixo Y')
ax1.plot(tempo_segundos, df['Eixo_Z_g'], color='orange', alpha=0.6, label='Eixo Z')
ax1.set_title(f'Análise Exploratória: {tipo_movimento} ({caminho_arquivo.split("/")[-1]}) - Canais Inerciais', fontsize=12)
ax1.set_ylabel('Aceleração Linear (g)')
ax1.set_ylim(-15, 15)
ax1.grid(True)
ax1.legend(loc='upper right')

# Subplot 2: Vetor Magnitude Resultante (SVM)
ax2.plot(tempo_segundos, df['SVM'], color='red', linewidth=1.8, label='SVM Resultante')
ax2.axhline(y=1.0, color='gray', linestyle=':', label='Gravidade Basal (1.0g)')
ax2.axhline(y=3.0, color='black', linestyle='--', label='Limiar Heurístico (3.0g)')
ax2.set_title(f'Vetor de Soma da Magnitude (SVM)', fontsize=12)
ax2.set_xlabel('Tempo (segundos)')
ax2.set_ylabel('Magnitude (g)')
ax2.set_ylim(0, 15)
ax2.set_xlim(0, 15)
ax2.grid(True)
ax2.legend(loc='upper right')

plt.tight_layout()
nome_saida = f'exploratoria_{caminho_arquivo.split("/")[-1].replace(".txt", "")}.png'
plt.savefig(nome_saida, dpi=300, bbox_inches='tight')
print(f"Figura final do Mês 4 salva como: {nome_saida}")