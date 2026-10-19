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

# 2. DIRETÓRIO DO DATASET E ARQUIVO DE SAÍDA
dataset_dir = 'SisFall_dataset'
arquivo_saida = 'dataset_sisfall_unificado.csv'
if os.path.exists(arquivo_saida):
    os.remove(arquivo_saida)

# Coleta de arquivos suportando tanto .txt (bruto original) quanto .csv (pré-processado)
# Caso ambos existam para o mesmo ensaio (ex: D01_SA04_R01.txt e .csv), prioriza o .txt bruto original
mapa_arquivos = {}
for pasta_raiz, _, arquivos in os.walk(dataset_dir):
    for arquivo in arquivos:
        ext = os.path.splitext(arquivo)[1].lower()
        if ext in ('.txt', '.csv'):
            nome_base = os.path.splitext(arquivo)[0]
            partes_nome = nome_base.split('_')
            if len(partes_nome) < 3 or not (partes_nome[0].startswith('D') or partes_nome[0].startswith('F')):
                continue
            chave = os.path.join(pasta_raiz, nome_base)
            # Prioriza .txt caso os dois formatos estejam presentes na mesma pasta
            if chave not in mapa_arquivos or ext == '.txt':
                mapa_arquivos[chave] = os.path.join(pasta_raiz, arquivo)

lista_caminhos = sorted(mapa_arquivos.values())
total_arquivos = len(lista_caminhos)
print(f"Total de ensaios identificados para processamento: {total_arquivos}")

buffer_dataframes = []
arquivos_processados = 0
total_linhas = 0
primeiro_lote = True

# 3. VARREDURA E PROCESSAMENTO EM LOTES (OTIMIZADO PARA RAM E VELOCIDADE)
for caminho_completo in lista_caminhos:
