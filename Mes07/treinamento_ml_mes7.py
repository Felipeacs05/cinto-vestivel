# ==============================================================================
# UNIVERSIDADE ESTADUAL DE FEIRA DE SANTANA (UEFS)
# Projeto de Iniciação Tecnológica (PIBITI/CNPq)
# Plano de Trabalho: Cinto Vestível com IoT para Monitoramento de Idosos
# Orientador: Prof. Dr. Germano Pinto Guedes
# Bolsista: Felipe Amorim do Carmo Silva
# ==============================================================================
# ARQUIVO: Mes07/treinamento_ml_mes7.py
# DESCRIÇÃO: Extrai as 16 características temporais em janelas de 2,0 s (400
#            amostras a 200 Hz) sobre os 4.505 ensaios filtrados da base SisFall,
#            salva a matriz 'features_sisfall_janelas.csv', treina o modelo
#            Random Forest para calcular a importância de Gini de cada atributo
#            e gera automaticamente o gráfico 'importancia_features_M7.png'.
# ==============================================================================

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from scipy.stats import skew, kurtosis
from sklearn.ensemble import RandomForestClassifier

warnings.filterwarnings('ignore')

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
CAMINHO_FEATURES = os.path.join(DIRETORIO_ATUAL, 'features_sisfall_janelas.csv')
CAMINHO_FIGURA_IMP = os.path.join(DIRETORIO_ATUAL, 'importancia_features_M7.png')

print("=================================================================")
print(" PIPELINE MÊS 07: EXTRAÇÃO DE 16 CARACTERÍSTICAS E IMPORTÂNCIA   ")
print("=================================================================\n")

# 1. PARÂMETROS DE PROCESSAMENTO DE SINAIS E JANELAMENTO
FS = 200.0                      # Taxa de amostragem do SisFall (200 Hz)
FC = 5.0                        # Frequência de corte Butterworth (5 Hz)
ORDEM = 4                       # Filtro de 4ª ordem
JANELA_AMOSTRAS = 400           # Janela de 2.0 segundos (400 amostras a 200 Hz)

COLUNAS_X = [
    'SVM_Mean', 'SVM_Std', 'SVM_Var', 'SVM_Max', 'SVM_Min', 'SVM_PtP',
    'SVM_Energy', 'SVM_Skew', 'SVM_Kurt',
    'X_Std', 'Y_Std', 'Z_Std', 'X_Var', 'Y_Var', 'Z_Var', 'SMA'
]


def extrair_features_janela(x_w, y_w, z_w, svm_w):
    """
    Extrai 16 características temporais e estatísticas de uma janela inercial de 2,0 s:
    - 9 Estatísticas do Vetor Resultante (SVM): Média, Desvio-Padrão, Variância,
      Máximo (Pico de Impacto), Mínimo (Queda Livre), Amplitude (Peak-to-Peak),
      Energia, Assimetria (Skewness) e Curtose (Kurtosis).
    - 6 Estatísticas Triaxiais (X, Y, Z): Desvio-Padrão e Variância de cada eixo.
    - 1 Área de Magnitude do Sinal (SMA - Signal Magnitude Area).
    """
    svm_mean = float(np.mean(svm_w))
    svm_std = float(np.std(svm_w))
    svm_var = float(np.var(svm_w))
    svm_max = float(np.max(svm_w))
    svm_min = float(np.min(svm_w))
    svm_ptp = svm_max - svm_min
    svm_energy = float(np.mean(svm_w ** 2))
    svm_skew = float(skew(svm_w)) if svm_std > 1e-6 else 0.0
    svm_kurt = float(kurtosis(svm_w)) if svm_std > 1e-6 else 0.0

    x_std = float(np.std(x_w))
    y_std = float(np.std(y_w))
    z_std = float(np.std(z_w))
    x_var = float(np.var(x_w))
    y_var = float(np.var(y_w))
    z_var = float(np.var(z_w))

    sma = float(np.mean(np.abs(x_w) + np.abs(y_w) + np.abs(z_w)))

    return {
        'SVM_Mean': svm_mean,
        'SVM_Std': svm_std,
        'SVM_Var': svm_var,
        'SVM_Max': svm_max,
        'SVM_Min': svm_min,
        'SVM_PtP': svm_ptp,
        'SVM_Energy': svm_energy,
        'SVM_Skew': svm_skew,
        'SVM_Kurt': svm_kurt,
        'X_Std': x_std,
        'Y_Std': y_std,
        'Z_Std': z_std,
        'X_Var': x_var,
        'Y_Var': y_var,
        'Z_Var': z_var,
        'SMA': sma
    }


def obter_ou_extrair_matriz_features():
    # Se a pasta bruta SisFall_dataset estiver presente, extrai dos arquivos brutos;
    # caso contrário, carrega o arquivo features_sisfall_janelas.csv já processado.
    possiveis_pastas = [
        os.path.join(DIRETORIO_ATUAL, 'SisFall_dataset'),
        os.path.join(DIRETORIO_ATUAL, '..', 'SisFall_dataset')
    ]
    dataset_dir = next((p for p in possiveis_pastas if os.path.exists(p)), None)

    if os.path.exists(CAMINHO_FEATURES) and dataset_dir is None:
        print(f"Carregando matriz de características existente: {CAMINHO_FEATURES}")
        return pd.read_csv(CAMINHO_FEATURES)

    if dataset_dir is None:
        raise FileNotFoundError("Nem 'SisFall_dataset' nem 'features_sisfall_janelas.csv' foram encontrados.")

    if os.path.exists(CAMINHO_FEATURES):
        print(f"Matriz '{CAMINHO_FEATURES}' já existe ({len(pd.read_csv(CAMINHO_FEATURES))} janelas).")
        return pd.read_csv(CAMINHO_FEATURES)

    b, a = butter(ORDEM, FC / (0.5 * FS), btype='low', analog=False)
    mapa_arquivos = {}
    for pasta_raiz, _, arquivos in os.walk(dataset_dir):
        for arquivo in arquivos:
            ext = os.path.splitext(arquivo)[1].lower()
            if ext in ('.txt', '.csv'):
                nome_base = os.path.splitext(arquivo)[0]
                partes = nome_base.split('_')
                if len(partes) < 3 or not (partes[0].startswith('D') or partes[0].startswith('F')):
                    continue
                chave = os.path.join(pasta_raiz, nome_base)
                if chave not in mapa_arquivos or ext == '.txt':
                    mapa_arquivos[chave] = os.path.join(pasta_raiz, arquivo)

    lista_caminhos = sorted(mapa_arquivos.values())
    print(f"Total de ensaios identificados no SisFall: {len(lista_caminhos)}")
    print("Filtrando (Butterworth 4ª ordem, 5 Hz) e extraindo 16 features por janela de 2,0 s...")

    registros_features = []
    for idx, caminho in enumerate(lista_caminhos, 1):
        nome_base, ext = os.path.splitext(os.path.basename(caminho))
        partes = nome_base.split('_')
        atividade, sujeito = partes[0], partes[1]
        classe = 1 if atividade.startswith('F') else 0
        grupo = 'Jovem' if sujeito.startswith('SA') else 'Idoso'

        try:
            if ext.lower() == '.csv':
                df_raw = pd.read_csv(caminho, usecols=[0, 1, 2])
                if 'ADXL345_Acc_X' in df_raw.columns:
                    x_g = pd.to_numeric(df_raw['ADXL345_Acc_X'], errors='coerce').to_numpy(dtype=np.float32)
                    y_g = pd.to_numeric(df_raw['ADXL345_Acc_Y'], errors='coerce').to_numpy(dtype=np.float32)
                    z_g = pd.to_numeric(df_raw['ADXL345_Acc_Z'], errors='coerce').to_numpy(dtype=np.float32)
                else:
                    df_raw = pd.read_csv(caminho, sep=',', header=None, usecols=[0, 1, 2], dtype=np.float32, engine='c')
                    x_g = df_raw[0].to_numpy() / 256.0
                    y_g = df_raw[1].to_numpy() / 256.0
                    z_g = df_raw[2].to_numpy() / 256.0
            else:
                df_raw = pd.read_csv(caminho, sep=',', header=None, usecols=[0, 1, 2], dtype=np.float32, engine='c')
                x_g = df_raw[0].to_numpy() / 256.0
                y_g = df_raw[1].to_numpy() / 256.0
                z_g = df_raw[2].to_numpy() / 256.0

            mask = ~(np.isnan(x_g) | np.isnan(y_g) | np.isnan(z_g))
            if not np.all(mask):
                x_g, y_g, z_g = x_g[mask], y_g[mask], z_g[mask]
            if len(x_g) < JANELA_AMOSTRAS:
                continue
        except Exception:
            continue

        x_f = filtfilt(b, a, x_g)
        y_f = filtfilt(b, a, y_g)
        z_f = filtfilt(b, a, z_g)
        svm_f = np.sqrt(x_f**2 + y_f**2 + z_f**2)

        idx_pico = int(np.argmax(svm_f))
        inicio = max(0, min(idx_pico - JANELA_AMOSTRAS // 2, len(svm_f) - JANELA_AMOSTRAS))
        fim = inicio + JANELA_AMOSTRAS

        feats = extrair_features_janela(x_f[inicio:fim], y_f[inicio:fim], z_f[inicio:fim], svm_f[inicio:fim])
        feats['Sujeito'] = sujeito
        feats['Grupo'] = grupo
        feats['Atividade'] = atividade
        feats['Classe'] = classe
        registros_features.append(feats)

        if idx % 1000 == 0:
            print(f"  -> [{idx}/{len(lista_caminhos)}] ensaios processados...")

    df_features = pd.DataFrame(registros_features)
    df_features.to_csv(CAMINHO_FEATURES, index=False)
    print(f"\nMatriz salva em '{CAMINHO_FEATURES}' ({len(df_features)} janelas).")
    return df_features


if __name__ == '__main__':
    df_features = obter_ou_extrair_matriz_features()
    print(f"Total de janelas: {len(df_features)} | Quedas (1): {(df_features['Classe']==1).sum()} | ADLs (0): {(df_features['Classe']==0).sum()}\n")

    # 2. CÁLCULO DA IMPORTÂNCIA RELATIVA DE GINI (RANDOM FOREST) E GERAÇÃO DO GRÁFICO DO MÊS 07
    X = df_features[COLUNAS_X].to_numpy()
    y = df_features['Classe'].to_numpy()

    rf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf.fit(X, y)

    imp = rf.feature_importances_
    idx_ordenado = np.argsort(imp)

    print("Ranking de Importância Relativa de Gini das 16 Features:")
    print("-" * 55)
    for i in reversed(idx_ordenado):
        print(f"  {COLUNAS_X[i]:<12} : {imp[i]*100:6.2f}%")
    print("-" * 55)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(np.array(COLUNAS_X)[idx_ordenado], imp[idx_ordenado] * 100, color='#2b5c8f', edgecolor='black', alpha=0.85)
    ax.set_xlabel('Importância Relativa de Gini (%)', fontsize=11)
    ax.set_title('Importância das Características Extraídas (Random Forest - SisFall)', fontsize=12, fontweight='bold')
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    for i, v in enumerate(imp[idx_ordenado] * 100):
        ax.text(v + 0.3, i, f'{v:.1f}%', va='center', fontsize=9)
    ax.set_xlim(0, max(imp * 100) * 1.15)
    plt.tight_layout()
    plt.savefig(CAMINHO_FIGURA_IMP, dpi=300)
    plt.close(fig)
    print(f"\n[OK] Gráfico de importância gerado automaticamente em: {CAMINHO_FIGURA_IMP}")
