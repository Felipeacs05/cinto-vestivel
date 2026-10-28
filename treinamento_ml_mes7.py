import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from scipy.stats import skew, kurtosis
from sklearn.model_selection import StratifiedKFold, cross_validate, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    ConfusionMatrixDisplay
)

warnings.filterwarnings('ignore')

print("=================================================================")
print(" PIPELINE MÊS 7 & MÊS 8: EXTRAÇÃO DE CARACTERÍSTICAS E TREINO ML ")
print("=================================================================\n")

# 1. PARÂMETROS DE PROCESSAMENTO DE SINAIS E JANELAMENTO
FS = 200.0                      # Taxa de amostragem do SisFall (200 Hz)
FC = 5.0                        # Frequência de corte Butterworth (5 Hz)
ORDEM = 4                       # Filtro de 4ª ordem
JANELA_AMOSTRAS = 400           # Janela de 2.0 segundos (400 amostras a 200 Hz)
PASSO_ADL = 400                 # Passo de 2.0s nas ADLs para balanceamento e eficiência

b, a = butter(ORDEM, FC / (0.5 * FS), btype='low', analog=False)
dataset_dir = 'SisFall_dataset'

# Mapeamento híbrido (.txt e .csv), priorizando .txt quando ambos existirem
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
print("Extraindo características matemáticas em janelas temporais...")

def extrair_features_janela(x_w, y_w, z_w, svm_w):
    """
    Extrai características temporais e estatísticas de uma janela inercial (TinyML-friendly):
    - Estatísticas do Vetor de Soma da Magnitude (SVM): Média, Desvio-Padrão, Variância,
      Máximo (Pico de Impacto), Mínimo (Queda Livre), Amplitude (Peak-to-Peak),
      Energia, Assimetria (Skewness) e Curtose (Kurtosis).
    - Estatísticas Triaxiais (X, Y, Z): Desvio-Padrão e Variância por eixo, além de SMA (Signal Magnitude Area).
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

    # Signal Magnitude Area (SMA)
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
