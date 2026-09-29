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

# 2. DIRETÓRIO DO DATASET E LISTA MESTRE
dataset_dir = 'SisFall_dataset'
lista_dataframes = []
arquivos_processados = 0

# 3. VARREDURA AUTOMÁTICA NAS PASTAS (SA e SE)
for pasta_raiz, _, arquivos in os.walk(dataset_dir):
    for arquivo in arquivos:
        if arquivo.endswith('.txt'):
            caminho_completo = os.path.join(pasta_raiz, arquivo)
            
            partes_nome = arquivo.replace('.txt', '').split('_')
            if len(partes_nome) < 3: 
                continue
                
            atividade = partes_nome[0]
            sujeito = partes_nome[1]
            
            # Lógica de Rotulação 
            classe = 1 if atividade.startswith('F') else 0
            grupo_idade = 'Jovem' if sujeito.startswith('SA') else 'Idoso'

            # 4. LEITURA E LIMPEZA
            nomes_colunas = ['ADXL_X', 'ADXL_Y', 'ADXL_Z', 'ITG_X', 'ITG_Y', 'ITG_Z', 'MMA_X', 'MMA_Y', 'MMA_Z']
            try:
                df = pd.read_csv(caminho_completo, sep=',', names=nomes_colunas, engine='python')
                df['MMA_Z'] = df['MMA_Z'].astype(str).str.replace(';', '').astype(float)
            except Exception as e:
                continue 
            
            # Conversão ADC -> g
            df['X_g'] = df['ADXL_X'] / 256.0
            df['Y_g'] = df['ADXL_Y'] / 256.0
            df['Z_g'] = df['ADXL_Z'] / 256.0
            
            # 5. APLICAÇÃO DO FILTRO NAS TRÊS DIMENSÕES
            x_filt = filtfilt(b, a, df['X_g'])
            y_filt = filtfilt(b, a, df['Y_g'])
            z_filt = filtfilt(b, a, df['Z_g'])
            
            svm_filt = np.sqrt(x_filt**2 + y_filt**2 + z_filt**2)
            
            # 6. ESTRUTURAÇÃO DO DATAFRAME LIMPO (Descartamos os dados brutos para economizar espaço)
            df_limpo = pd.DataFrame({
                'X_Filt': x_filt,
                'Y_Filt': y_filt,
                'Z_Filt': z_filt,
                'SVM_Filt': svm_filt,
                'Sujeito': sujeito,
                'Grupo': grupo_idade,
                'Atividade': atividade,
                'Classe': classe
            })
            
            lista_dataframes.append(df_limpo)
            arquivos_processados += 1
            
            # Feedback visual no terminal a cada 500 arquivos processados
            if arquivos_processados % 500 == 0:
                print(f"[{arquivos_processados}/4505] arquivos processados...")

print(f"\nVarredura concluída! {arquivos_processados} arquivos lidos.")
print("Concatenando matrizes... (isso pode exigir memória RAM)")
df_mestre = pd.concat(lista_dataframes, ignore_index=True)

print(f"Matriz Mestre criada com sucesso! Total de amostras temporais: {len(df_mestre)} linhas.")
print("Salvando o arquivo CSV unificado no disco...")

df_mestre.to_csv('dataset_sisfall_unificado.csv', index=False)

print("SUCESSO! Arquivo 'dataset_sisfall_unificado.csv' gerado.")
print("O Mês 5 está 100% concluído!")