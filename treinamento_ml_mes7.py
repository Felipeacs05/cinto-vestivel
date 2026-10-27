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
