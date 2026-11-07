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
dataset_dir = 'SisFall_dataset' if os.path.exists('SisFall_dataset') else os.path.join('..', 'SisFall_dataset')
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
    arquivo = os.path.basename(caminho_completo)
    nome_base, ext = os.path.splitext(arquivo)
    partes_nome = nome_base.split('_')

    atividade = partes_nome[0]
    sujeito = partes_nome[1]

    # Lógica de Rotulação
    classe = 1 if atividade.startswith('F') else 0
    grupo_idade = 'Jovem' if sujeito.startswith('SA') else 'Idoso'

    # 4. LEITURA E CONVERSÃO (SUPORTE HÍBRIDO .TXT E .CSV)
    try:
        if ext.lower() == '.csv':
            df_raw = pd.read_csv(caminho_completo, usecols=[0, 1, 2])
            if 'ADXL345_Acc_X' in df_raw.columns:
                # .csv pré-processado já está convertido em g
                x_g = pd.to_numeric(df_raw['ADXL345_Acc_X'], errors='coerce').to_numpy(dtype=np.float32)
                y_g = pd.to_numeric(df_raw['ADXL345_Acc_Y'], errors='coerce').to_numpy(dtype=np.float32)
                z_g = pd.to_numeric(df_raw['ADXL345_Acc_Z'], errors='coerce').to_numpy(dtype=np.float32)
            else:
                df_raw = pd.read_csv(caminho_completo, sep=',', header=None, usecols=[0, 1, 2], dtype=np.float32, engine='c')
                x_g = df_raw[0].to_numpy() / 256.0
                y_g = df_raw[1].to_numpy() / 256.0
                z_g = df_raw[2].to_numpy() / 256.0
        else:
            # Leitura rápida via engine C apenas das 3 colunas do ADXL345
            df_raw = pd.read_csv(caminho_completo, sep=',', header=None, usecols=[0, 1, 2], dtype=np.float32, engine='c')
            x_g = df_raw[0].to_numpy() / 256.0
            y_g = df_raw[1].to_numpy() / 256.0
            z_g = df_raw[2].to_numpy() / 256.0

        mask_valido = ~(np.isnan(x_g) | np.isnan(y_g) | np.isnan(z_g))
        if not np.all(mask_valido):
            x_g, y_g, z_g = x_g[mask_valido], y_g[mask_valido], z_g[mask_valido]

        if len(x_g) <= 15:
            continue
    except Exception:
        continue

    # 5. APLICAÇÃO DO FILTRO NAS TRÊS DIMENSÕES
    x_filt = filtfilt(b, a, x_g).astype(np.float32)
    y_filt = filtfilt(b, a, y_g).astype(np.float32)
    z_filt = filtfilt(b, a, z_g).astype(np.float32)

    svm_filt = np.sqrt(x_filt**2 + y_filt**2 + z_filt**2).astype(np.float32)

    # 6. ESTRUTURAÇÃO DO DATAFRAME LIMPO
    df_limpo = pd.DataFrame({
        'X_Filt': np.round(x_filt, 5),
        'Y_Filt': np.round(y_filt, 5),
        'Z_Filt': np.round(z_filt, 5),
        'SVM_Filt': np.round(svm_filt, 5),
        'Sujeito': sujeito,
        'Grupo': grupo_idade,
        'Atividade': atividade,
        'Classe': classe
    })

    buffer_dataframes.append(df_limpo)
    arquivos_processados += 1
    total_linhas += len(df_limpo)

    # Grava em lotes de 500 arquivos para economizar memória RAM
    if arquivos_processados % 500 == 0:
        print(f"[{arquivos_processados}/{total_arquivos}] arquivos processados...")
        df_lote = pd.concat(buffer_dataframes, ignore_index=True)
        df_lote.to_csv(arquivo_saida, mode='w' if primeiro_lote else 'a', index=False, header=primeiro_lote)
        primeiro_lote = False
        buffer_dataframes.clear()

# Grava o restante do buffer
if buffer_dataframes:
    df_lote = pd.concat(buffer_dataframes, ignore_index=True)
    df_lote.to_csv(arquivo_saida, mode='w' if primeiro_lote else 'a', index=False, header=primeiro_lote)
    buffer_dataframes.clear()

print(f"\nVarredura concluída! {arquivos_processados} arquivos lidos.")
print(f"Matriz Mestre criada com sucesso! Total de amostras temporais: {total_linhas} linhas.")
print(f"SUCESSO! Arquivo '{arquivo_saida}' gerado.")
print("O Mês 5 está 100% concluído!")
