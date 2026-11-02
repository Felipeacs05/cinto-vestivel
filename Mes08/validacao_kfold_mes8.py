import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold, cross_validate, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    ConfusionMatrixDisplay
)

warnings.filterwarnings('ignore')

print("=================================================================")
print(" MÊS 08: VALIDAÇÃO CRUZADA (10-FOLD) E SELEÇÃO DE MODELO TINYML ")
print("=================================================================\n")

caminho_features = 'features_sisfall_janelas.csv'
if not os.path.exists(caminho_features):
    caminho_features = os.path.join('..', 'Mes07', 'features_sisfall_janelas.csv')
if not os.path.exists(caminho_features):
    caminho_features = os.path.join('..', 'features_sisfall_janelas.csv')

df_features = pd.read_csv(caminho_features)
colunas_x = [
    'SVM_Mean', 'SVM_Std', 'SVM_Var', 'SVM_Max', 'SVM_Min', 'SVM_PtP',
    'SVM_Energy', 'SVM_Skew', 'SVM_Kurt',
    'X_Std', 'Y_Std', 'Z_Std', 'X_Var', 'Y_Var', 'Z_Var', 'SMA'
]

X = df_features[colunas_x].to_numpy()
y = df_features['Classe'].to_numpy()

skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

modelos = {
    'SVM (RBF)': Pipeline([
        ('scaler', StandardScaler()),
        ('clf', SVC(kernel='rbf', C=10.0, gamma='scale', random_state=42))
    ]),
    'Random Forest': RandomForestClassifier(
