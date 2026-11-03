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
        n_estimators=100, max_depth=12, random_state=42, n_jobs=-1
    )
}

resultados_cv = {}
predicoes_globais = {}

for nome, modelo in modelos.items():
    cv_res = cross_validate(
        modelo, X, y, cv=skf,
        scoring=['accuracy', 'precision', 'recall', 'f1'],
        n_jobs=-1
    )
    y_pred = cross_val_predict(modelo, X, y, cv=skf, n_jobs=-1)
    predicoes_globais[nome] = y_pred
    resultados_cv[nome] = cv_res

    print(f"--- {nome} (10-Fold Stratified Cross-Validation) ---")
    print(f"Acurácia:               {accuracy_score(y, y_pred)*100:.2f}% (± {cv_res['test_accuracy'].std()*100:.2f}%)")
    print(f"Precisão:               {precision_score(y, y_pred)*100:.2f}% (± {cv_res['test_precision'].std()*100:.2f}%)")
    print(f"Recall (Sensibilidade): {recall_score(y, y_pred)*100:.2f}% (± {cv_res['test_recall'].std()*100:.2f}%)")
    print(f"F1-Score:               {f1_score(y, y_pred)*100:.2f}% (± {cv_res['test_f1'].std()*100:.2f}%)")
    print("Matriz de Confusão Acumulada:")
    print(confusion_matrix(y, y_pred))
    print()

folds = np.arange(1, 11)
df_relatorio = pd.DataFrame({
    'Fold': folds,
    'SVM_Accuracy': np.round(resultados_cv['SVM (RBF)']['test_accuracy'] * 100, 2),
    'SVM_Precision': np.round(resultados_cv['SVM (RBF)']['test_precision'] * 100, 2),
    'SVM_Recall': np.round(resultados_cv['SVM (RBF)']['test_recall'] * 100, 2),
    'SVM_F1': np.round(resultados_cv['SVM (RBF)']['test_f1'] * 100, 2),
    'RF_Accuracy': np.round(resultados_cv['Random Forest']['test_accuracy'] * 100, 2),
    'RF_Precision': np.round(resultados_cv['Random Forest']['test_precision'] * 100, 2),
    'RF_Recall': np.round(resultados_cv['Random Forest']['test_recall'] * 100, 2),
    'RF_F1': np.round(resultados_cv['Random Forest']['test_f1'] * 100, 2),
})
df_relatorio.to_csv('metricas_10fold_M8.csv', index=False)
print("Tabela de métricas por partição salva em 'metricas_10fold_M8.csv'.")
