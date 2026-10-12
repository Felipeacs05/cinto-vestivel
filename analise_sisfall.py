import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

    # Limpeza e conversão ADC -> g (ADXL345: 256 LSB/g)
    for col in ['ADXL_X', 'ADXL_Y', 'ADXL_Z']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['ADXL_X', 'ADXL_Y', 'ADXL_Z'])

    df['Eixo_X_g'] = df['ADXL_X'] / 256.0
    df['Eixo_Y_g'] = df['ADXL_Y'] / 256.0
    df['Eixo_Z_g'] = df['ADXL_Z'] / 256.0
    return df, caminho_arquivo

# Caminho do arquivo a ser analisado (aceita .txt ou .csv automaticamente)
caminho_arquivo = 'SisFall_dataset/SE01/D01_SE01_R01.txt'
df, caminho_real = carregar_arquivo_sisfall(caminho_arquivo)
df['SVM'] = np.sqrt(df['Eixo_X_g']**2 + df['Eixo_Y_g']**2 + df['Eixo_Z_g']**2)

tempo_segundos = np.arange(len(df)) / 200.0
nome_base = os.path.splitext(os.path.basename(caminho_real))[0]
tipo_movimento = "Queda" if nome_base.startswith("F") else "Atividade Diária"

# Criando 2 subplots verticais para desacoplar as linhas
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Subplot 1: Componentes Triaxiais
ax1.plot(tempo_segundos, df['Eixo_X_g'], color='blue', alpha=0.6, label='Eixo X')
ax1.plot(tempo_segundos, df['Eixo_Y_g'], color='green', alpha=0.6, label='Eixo Y')
ax1.plot(tempo_segundos, df['Eixo_Z_g'], color='orange', alpha=0.6, label='Eixo Z')
ax1.set_title(f'Análise Exploratória: {tipo_movimento} ({os.path.basename(caminho_real)}) - Canais Inerciais', fontsize=12)
ax1.set_ylabel('Aceleração Linear (g)')
ax1.set_ylim(-15, 15)
ax1.grid(True)
ax1.legend(loc='upper right')

# Subplot 2: Vetor Magnitude Resultante (SVM)
ax2.plot(tempo_segundos, df['SVM'], color='red', linewidth=1.8, label='SVM Resultante')
ax2.axhline(y=1.0, color='gray', linestyle=':', label='Gravidade Basal (1.0g)')
ax2.axhline(y=3.0, color='black', linestyle='--', label='Limiar Heurístico (3.0g)')
ax2.set_title('Vetor de Soma da Magnitude (SVM)', fontsize=12)
ax2.set_xlabel('Tempo (segundos)')
ax2.set_ylabel('Magnitude (g)')
ax2.set_ylim(0, 15)
ax2.set_xlim(0, 15)
ax2.grid(True)
ax2.legend(loc='upper right')

plt.tight_layout()
nome_saida = f'exploratoria_{nome_base}.png'
plt.savefig(nome_saida, dpi=300, bbox_inches='tight')
print(f"Figura final do Mês 4 salva como: {nome_saida}")
