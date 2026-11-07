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
dataset_dir = 'SisFall_dataset' if os.path.exists('SisFall_dataset') else os.path.join('..', 'SisFall_dataset')

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
        'X_Var': x_var,
        'Y_Var': y_var,
        'Z_Var': z_var,
        'SMA': sma
    }

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

    # Filtragem Butterworth de 4ª ordem (5 Hz)
    x_f = filtfilt(b, a, x_g)
    y_f = filtfilt(b, a, y_g)
    z_f = filtfilt(b, a, z_g)
    svm_f = np.sqrt(x_f**2 + y_f**2 + z_f**2)

    if classe == 1:
        # Em arquivos de Queda (F), extrai a janela temporal de 2.0s centrada no pico de impacto máximo
        idx_pico = int(np.argmax(svm_f))
        inicio = max(0, min(idx_pico - JANELA_AMOSTRAS // 2, len(svm_f) - JANELA_AMOSTRAS))
        fim = inicio + JANELA_AMOSTRAS

        feats = extrair_features_janela(x_f[inicio:fim], y_f[inicio:fim], z_f[inicio:fim], svm_f[inicio:fim])
        feats['Sujeito'] = sujeito
        feats['Grupo'] = grupo
        feats['Atividade'] = atividade
        feats['Classe'] = 1
        registros_features.append(feats)
    else:
        # Em arquivos de Atividades Diárias (D), extrai a janela de maior excitação dinâmica (hard negative)
        idx_pico = int(np.argmax(svm_f))
        inicio_pico = max(0, min(idx_pico - JANELA_AMOSTRAS // 2, len(svm_f) - JANELA_AMOSTRAS))
        fim_pico = inicio_pico + JANELA_AMOSTRAS

        feats_pico = extrair_features_janela(
            x_f[inicio_pico:fim_pico], y_f[inicio_pico:fim_pico], z_f[inicio_pico:fim_pico], svm_f[inicio_pico:fim_pico]
        )
        feats_pico['Sujeito'] = sujeito
        feats_pico['Grupo'] = grupo
        feats_pico['Atividade'] = atividade
        feats_pico['Classe'] = 0
        registros_features.append(feats_pico)

    if idx % 1000 == 0:
        print(f"  -> [{idx}/{len(lista_caminhos)}] ensaios processados...")

df_features = pd.DataFrame(registros_features)
arquivo_features = 'features_sisfall_janelas.csv'
df_features.to_csv(arquivo_features, index=False)
print(f"\nMatriz de Características salva em '{arquivo_features}' ({len(df_features)} janelas extraídas).")
print(f"Distribuição de Classes: Quedas (1) = {(df_features['Classe']==1).sum()} | ADLs (0) = {(df_features['Classe']==0).sum()}\n")

# 2. TREINAMENTO E VALIDAÇÃO CRUZADA K-FOLD (10-FOLD) - MÊS 7 E MÊS 8
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

resultados_metricas = {}
predicoes_modelos = {}

print("Executando Validação Cruzada Estratificada (10-Fold)...")
for nome, modelo in modelos.items():
    y_pred = cross_val_predict(modelo, X, y, cv=skf, n_jobs=-1)
    predicoes_modelos[nome] = y_pred

    acc = accuracy_score(y, y_pred)
    prec = precision_score(y, y_pred)
    rec = recall_score(y, y_pred)
    f1 = f1_score(y, y_pred)

    resultados_metricas[nome] = {
        'Acurácia': acc,
        'Precisão': prec,
        'Recall (Sensibilidade)': rec,
        'F1-Score': f1
    }

    print(f"\n--- Resultados 10-Fold: {nome} ---")
    print(f"Acurácia:               {acc*100:.2f}%")
    print(f"Precisão:               {prec*100:.2f}%")
    print(f"Recall (Sensibilidade): {rec*100:.2f}%")
    print(f"F1-Score:               {f1*100:.2f}%")
    print("Matriz de Confusão:")
    print(confusion_matrix(y, y_pred))

# 3. GERAÇÃO DO GRÁFICO COMPARATIVO DE MATRIZES DE CONFUSÃO E MÉTRICAS
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
for ax, (nome, y_pred) in zip(axes, predicoes_modelos.items()):
    cm = confusion_matrix(y, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['ADL (Normal)', 'Queda'])
    disp.plot(ax=ax, cmap='Blues', colorbar=False, values_format='d')
    m = resultados_metricas[nome]
    ax.set_title(
        f"{nome} (10-Fold CV)\nAcc: {m['Acurácia']*100:.2f}% | Recall: {m['Recall (Sensibilidade)']*100:.2f}% | F1: {m['F1-Score']*100:.2f}%",
        fontsize=11
    )
    ax.set_xlabel('Classe Predita')
    ax.set_ylabel('Classe Real')

plt.suptitle('Validação Cruzada (10-Fold) - Detecção de Quedas (SisFall)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('comparativo_modelos_ml_M7_M8.png', dpi=300, bbox_inches='tight')
print("\nGráfico salvo como 'comparativo_modelos_ml_M7_M8.png'!")
