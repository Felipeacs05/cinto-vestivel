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


# Utilizaremos o Acelerômetro 1 (ADXL345) porque ele mede até 16g (ideal para captar quedas brutais).
# Resolução de 13 bits para uma faixa de 32g (de -16g a +16g): (2^13) / 32 = 256 LSB/g.
# Portanto, dividimos os valores por 256 para obter a força em g.
df['Eixo_X_g'] = df['ADXL_X'] / 256.0
df['Eixo_Y_g'] = df['ADXL_Y'] / 256.0
df['Eixo_Z_g'] = df['ADXL_Z'] / 256.0

# Cálculo do SVM (Signal Vector Magnitude) que ja foi implementado no ESP32
df['SVM'] = np.sqrt(df['Eixo_X_g']**2 + df['Eixo_Y_g']**2 + df['Eixo_Z_g']**2)

