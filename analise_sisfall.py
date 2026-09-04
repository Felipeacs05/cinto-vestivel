import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Análise da Queda Frontal (F01) do Adulto Jovem 01 (SA01), Repetição 1 (R01)
caminho_arquivo = 'SisFall_dataset/SA01/F01_SA01_R01.txt'

# O arquivo usa vírgulas para separar colunas e tem um ponto e vírgula no final de cada linha.
# Lemos as 9 primeiras colunas correspondentes aos sensores.
nomes_colunas = ['ADXL_X', 'ADXL_Y', 'ADXL_Z', 'ITG_X', 'ITG_Y', 'ITG_Z', 'MMA_X', 'MMA_Y', 'MMA_Z']

# Lendo o arquivo. O separador real é a vírgula.
df = pd.read_csv(caminho_arquivo, sep=',', names=nomes_colunas, engine='python')

# Limpeza: a última coluna vem com o ';' anexado aos números. Vamos remover e converter para float.
df['MMA_Z'] = df['MMA_Z'].astype(str).str.replace(';', '').astype(float)

