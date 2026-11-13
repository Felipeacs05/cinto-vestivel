# ==============================================================================
# UNIVERSIDADE ESTADUAL DE FEIRA DE SANTANA (UEFS)
# Projeto de Iniciação Tecnológica (PIBITI/CNPq)
# Plano de Trabalho: Cinto Vestível com IoT para Monitoramento de Idosos
# Orientador: Prof. Dr. Germano Pinto Guedes
# Bolsista: Felipe Amorim do Carmo Silva
# ==============================================================================
# ARQUIVO: Mes08/validacao_kfold_mes8.py
# DESCRIÇÃO: Executa a Validação Cruzada Estratificada de 10 Pastas (10-Fold
#            Stratified Cross-Validation) para os modelos SVM (RBF) e Random
#            Forest sobre as 4.505 janelas do SisFall e gera automaticamente:
#              1. 'metricas_10fold_M8.csv' (desempenho nas 10 pastas de teste);
#              2. 'comparativo_modelos_ml_M7_M8.png' (matrizes de confusão);
#              3. 'estabilidade_kfold_M8.png' (F1-Score por Fold vs meta 90%).
# ==============================================================================

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

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
CAMINHO_CSV_METRICAS = os.path.join(DIRETORIO_ATUAL, 'metricas_10fold_M8.csv')
CAMINHO_FIG_MATRIZES = os.path.join(DIRETORIO_ATUAL, 'comparativo_modelos_ml_M7_M8.png')
CAMINHO_FIG_ESTABILIDADE = os.path.join(DIRETORIO_ATUAL, 'estabilidade_kfold_M8.png')

print("=================================================================")
print(" MÊS 08: VALIDAÇÃO CRUZADA (10-FOLD) E SELEÇÃO DE MODELO TINYML ")
print("=================================================================\n")

possiveis_features = [
    os.path.join(DIRETORIO_ATUAL, '..', 'Mes07', 'features_sisfall_janelas.csv'),
    os.path.join(DIRETORIO_ATUAL, 'features_sisfall_janelas.csv'),
]
caminho_features = next((p for p in possiveis_features if os.path.exists(p)), None)
if caminho_features is None:
    raise FileNotFoundError("Arquivo 'features_sisfall_janelas.csv' não encontrado em Mes07/.")

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
metricas_globais = {}

for nome, modelo in modelos.items():
    cv_res = cross_validate(
        modelo, X, y, cv=skf,
        scoring=['accuracy', 'precision', 'recall', 'f1'],
        n_jobs=-1
    )
    y_pred = cross_val_predict(modelo, X, y, cv=skf, n_jobs=-1)
    predicoes_globais[nome] = y_pred
    resultados_cv[nome] = cv_res

    acc = accuracy_score(y, y_pred)
    prec = precision_score(y, y_pred)
    rec = recall_score(y, y_pred)
    f1 = f1_score(y, y_pred)
    metricas_globais[nome] = {'Acurácia': acc, 'Precisão': prec, 'Recall': rec, 'F1': f1}

    print(f"--- {nome} (10-Fold Stratified Cross-Validation) ---")
    print(f"Acurácia:               {acc*100:.2f}% (± {cv_res['test_accuracy'].std()*100:.2f}%)")
    print(f"Precisão:               {prec*100:.2f}% (± {cv_res['test_precision'].std()*100:.2f}%)")
    print(f"Recall (Sensibilidade): {rec*100:.2f}% (± {cv_res['test_recall'].std()*100:.2f}%)")
    print(f"F1-Score:               {f1*100:.2f}% (± {cv_res['test_f1'].std()*100:.2f}%)")
    print("Matriz de Confusão Acumulada:")
    print(confusion_matrix(y, y_pred))
    print()

# 1. SALVA TABELA DAS 10 PASTAS (10 FOLDS) EM CSV
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
df_relatorio.to_csv(CAMINHO_CSV_METRICAS, index=False)
print(f"[OK] Tabela de métricas das 10 partições salva em: {CAMINHO_CSV_METRICAS}")

# 2. GERA GRÁFICO DAS MATRIZES DE CONFUSÃO (comparativo_modelos_ml_M7_M8.png)
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
for ax, (nome, y_pred) in zip(axes, predicoes_globais.items()):
    cm = confusion_matrix(y, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['ADL (Normal)', 'Queda'])
    disp.plot(ax=ax, cmap='Blues', colorbar=False, values_format='d')
    m = metricas_globais[nome]
    ax.set_title(
        f"{nome} (10-Fold CV)\nAcc: {m['Acurácia']*100:.2f}% | Recall: {m['Recall']*100:.2f}% | F1: {m['F1']*100:.2f}%",
        fontsize=11
    )
    ax.set_xlabel('Classe Predita')
    ax.set_ylabel('Classe Real')

plt.suptitle('Validação Cruzada (10-Fold) - Detecção de Quedas (SisFall)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(CAMINHO_FIG_MATRIZES, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"[OK] Gráfico de matrizes de confusão salvo em: {CAMINHO_FIG_MATRIZES}")

# 3. GERA GRÁFICO DE ESTABILIDADE POR FOLD (estabilidade_kfold_M8.png)
mean_svm = resultados_cv['SVM (RBF)']['test_f1'].mean() * 100
mean_rf = resultados_cv['Random Forest']['test_f1'].mean() * 100

fig2, ax2 = plt.subplots(figsize=(11, 5.5))
ax2.plot(
    folds, resultados_cv['SVM (RBF)']['test_f1'] * 100,
    marker='o', linewidth=2, color='#1b4f72',
    label=f'SVM RBF - F1-Score (Média: {mean_svm:.2f}%)'
)
ax2.plot(
    folds, resultados_cv['Random Forest']['test_f1'] * 100,
    marker='s', linewidth=2, linestyle='--', color='#922b21',
    label=f'Random Forest - F1-Score (Média: {mean_rf:.2f}%)'
)
ax2.axhline(y=90.0, color='gray', linestyle=':', linewidth=1.5, label='Meta Mínima do Plano de Trabalho (90,0%)')
ax2.set_xticks(folds)
ax2.set_xticklabels([f'Fold {i}' for i in folds])
ax2.set_ylim(88, 101)
ax2.set_ylabel('F1-Score (%)', fontsize=11)
ax2.set_xlabel('Partições da Validação Cruzada Estratificada (10-Fold)', fontsize=11)
ax2.set_title('Estabilidade do F1-Score por Partição (10-Fold Cross-Validation - Mês 8)', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.4)
ax2.legend(loc='lower right')
plt.tight_layout()
plt.savefig(CAMINHO_FIG_ESTABILIDADE, dpi=300)
plt.close(fig2)
print(f"[OK] Gráfico de estabilidade 10-Fold salvo em: {CAMINHO_FIG_ESTABILIDADE}")
