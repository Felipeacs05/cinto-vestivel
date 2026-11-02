# UNIVERSIDADE ESTADUAL DE FEIRA DE SANTANA (UEFS)
**Pró-Reitoria de Pesquisa e Pós-Graduação (PPPG)**  
**Programa Institucional de Bolsas de Iniciação em Desenvolvimento Tecnológico e Inovação (PIBITI/CNPq)**  
**Edital PPPG-IT/UEFS Nº 02/2026**

**Projeto de Pesquisa:** Sistemas Embarcados, Internet das Coisas (IoT) e Inteligência Artificial Aplicada à Saúde Assistiva  
**Plano de Trabalho:** Cinto Vestível com IoT para Monitoramento de Idosos  
**Orientador:** Prof. Dr. Germano Pinto Guedes (`germano@uefs.br`)  
**Bolsista:** Felipe Amorim do Carmo Silva (`felipedocarmo05@gmail.com`)  

---

# RELATÓRIO TÉCNICO PARCIAL — MÊS 07
**Período de Referência:** Mês 07 do Cronograma de Execução  
**Etapa:** Extração de Características (*Feature Extraction*) em Janelas Temporais e Treinamento de Modelos Supervisionados de Machine Learning  
**Artefatos Associados:** [`treinamento_ml_mes7.py`](treinamento_ml_mes7.py), [`features_sisfall_janelas.csv`](features_sisfall_janelas.csv), [`importancia_features_M7.png`](importancia_features_M7.png)

---

## RESUMO

Este relatório descreve a metodologia e a implementação referentes ao sétimo mês de execução do plano de trabalho, compreendendo a segmentação em janelas temporais dos sinais inerciais filtrados, a extração de características estatísticas e energéticas (*Feature Extraction*) e o treinamento de classificadores supervisionados de Aprendizado de Máquina (**Máquinas de Vetores de Suporte — SVM** e **Random Forest**) com a biblioteca `scikit-learn`. Adotou-se uma janela temporal de $2,0\text{ segundos}$ ($N = 400\text{ amostras}$ a $200\text{ Hz}$), reduzindo a dimensionalidade de cada ensaio para um vetor compacto de **16 descritores matemáticos** adequados para execução em microcontroladores (*TinyML*). A matriz resultante de $4.505\text{ janelas}$ foi armazenada em [`features_sisfall_janelas.csv`](features_sisfall_janelas.csv).

**Palavras-chave:** Extração de Características. Janelamento Temporal. Aprendizado de Máquina Supervisionado. Random Forest. SVM.

---

## 1 FUNDAMENTAÇÃO DO JANELAMENTO TEMPORAL E ENGENHARIA DE ATRIBUTOS

Classificadores embarcados voltados ao reconhecimento de padrões cinemáticos não operam sobre leituras instantâneas isoladas, visto que uma única amostra de aceleração elevada é incapaz de diferenciar o impacto de um salto voluntário (ADL) de uma colisão acidental contra o solo. A assinatura física de uma queda desenrola-se ao longo de um intervalo contínuo que engloba a perda de sustentação (queda livre), o choque mecânico e a subsequente mudança de orientação gravitacional do tronco (IGUAL; MEDRANO; PLAZA, 2013; SUCERQUIA; LÓPEZ; VARGAS-BONILLA, 2017).

Para capturar esse fenômeno completo mantendo reduzido consumo de memória SRAM no ESP32, definiu-se uma janela de observação de $T_w = 2,0\text{ segundos}$ ($N = 400\text{ amostras}$ a $f_s = 200\text{ Hz}$) centrada no instante de máxima excitação dinâmica ($\arg\max \text{SVM}$) de cada um dos 4.505 ensaios filtrados pelo Butterworth de 4ª ordem ($5\text{ Hz}$). Essa estratégia submete o classificador ao teste mais rigoroso possível contra falsos positivos (*hard negatives*): nas 2.707 Atividades de Vida Diária (`Classe = 0`), a janela recai exatamente sobre o momento de maior impacto da atividade cotidiana (como o instante de aterrissagem de um salto `D19`, corrida `D04` ou sentar-se abruptamente `D08`/`D10`).

### 1.1 Formulação Matemática das 16 Características Extraídas

De cada janela contendo $N = 400$ vetores triaxiais $(x_i, y_i, z_i)$ e magnitude resultante $s_i = \sqrt{x_i^2 + y_i^2 + z_i^2}$, foram extraídos 16 descritores no domínio do tempo:

1. **Média da Magnitude ($\mu_{\text{SVM}}$):** $\frac{1}{N}\sum_{i=1}^{N} s_i$
2. **Desvio-Padrão da Magnitude ($\sigma_{\text{SVM}}$):** $\sqrt{\frac{1}{N}\sum_{i=1}^{N} (s_i - \mu_{\text{SVM}})^2}$
3. **Variância da Magnitude ($\sigma^2_{\text{SVM}}$):** $\frac{1}{N}\sum_{i=1}^{N} (s_i - \mu_{\text{SVM}})^2$
4. **Pico Máximo de Impacto ($\text{SVM}_{\max}$):** $\max_{1 \le i \le N} (s_i)$
5. **Vale Mínimo de Queda Livre ($\text{SVM}_{\min}$):** $\min_{1 \le i \le N} (s_i)$
6. **Amplitude Pico-a-Pico ($\text{SVM}_{\text{PtP}}$):** $\text{SVM}_{\max} - \text{SVM}_{\min}$
7. **Energia Quadrática Média ($E_{\text{SVM}}$):** $\frac{1}{N}\sum_{i=1}^{N} s_i^2$
8. **Assimetria Estatística (*Skewness* — $\gamma_1$):** $\frac{\frac{1}{N}\sum_{i=1}^{N}(s_i - \mu_{\text{SVM}})^3}{\sigma_{\text{SVM}}^3}$
9. **Curtose (*Kurtosis* de Fisher — $\gamma_2$):** $\frac{\frac{1}{N}\sum_{i=1}^{N}(s_i - \mu_{\text{SVM}})^4}{\sigma_{\text{SVM}}^4} - 3$
10. **Desvios-Padrão Direcionais ($\sigma_X, \sigma_Y, \sigma_Z$) e Variâncias Direcionais ($\sigma^2_X, \sigma^2_Y, \sigma^2_Z$):** Medem a dispersão individual de cada eixo ortogonal, capturando a inversão do vetor gravidade quando o indivíduo passa da postura ereta para a horizontal;
11. **Área de Magnitude do Sinal (*Signal Magnitude Area* — $\text{SMA}$):**

$$\text{SMA} = \frac{1}{N} \sum_{i=1}^{N} \left( |x_i| + |y_i| + |z_i| \right)$$

---

## 2 IMPLEMENTAÇÃO COMPUTACIONAL (`treinamento_ml_mes7.py`)

A Listagem 1 apresenta a função de extração vetorial e a configuração dos estimadores supervisionados implementadas em [`treinamento_ml_mes7.py`](treinamento_ml_mes7.py).

### Listagem 1 — Função de Extração de Características e Pipeline de Treinamento (`treinamento_ml_mes7.py`)

```python
def extrair_features_janela(x_w, y_w, z_w, svm_w):
    svm_mean = float(np.mean(svm_w))
    svm_std = float(np.std(svm_w))
    svm_var = float(np.var(svm_w))
    svm_max = float(np.max(svm_w))
    svm_min = float(np.min(svm_w))
    svm_ptp = svm_max - svm_min
    svm_energy = float(np.mean(svm_w ** 2))
    svm_skew = float(skew(svm_w)) if svm_std > 1e-6 else 0.0
    svm_kurt = float(kurtosis(svm_w)) if svm_std > 1e-6 else 0.0

    x_std, y_std, z_std = float(np.std(x_w)), float(np.std(y_w)), float(np.std(z_w))
    x_var, y_var, z_var = float(np.var(x_w)), float(np.var(y_w)), float(np.var(z_w))
    sma = float(np.mean(np.abs(x_w) + np.abs(y_w) + np.abs(z_w)))

    return {
        'SVM_Mean': svm_mean, 'SVM_Std': svm_std, 'SVM_Var': svm_var,
        'SVM_Max': svm_max, 'SVM_Min': svm_min, 'SVM_PtP': svm_ptp,
        'SVM_Energy': svm_energy, 'SVM_Skew': svm_skew, 'SVM_Kurt': svm_kurt,
        'X_Std': x_std, 'Y_Std': y_std, 'Z_Std': z_std,
        'X_Var': x_var, 'Y_Var': y_var, 'Z_Var': z_var, 'SMA': sma
    }

modelos = {
    'SVM (RBF)': Pipeline([
        ('scaler', StandardScaler()),
        ('clf', SVC(kernel='rbf', C=10.0, gamma='scale', random_state=42))
    ]),
    'Random Forest': RandomForestClassifier(
        n_estimators=100, max_depth=12, random_state=42, n_jobs=-1
    )
}
```

---

## 3 ANÁLISE DE IMPORTÂNCIA DAS CARACTERÍSTICAS

A partir do ajuste do classificador **Random Forest** sobre a matriz de características (`4.505 janelas`, sendo `2.707 ADLs` e `1.798 Quedas`), avaliou-se o ganho de pureza de Gini proporcionado por cada variável, conforme ilustrado na Figura 1.

![Figura 1 — Importância relativa das 16 características extraídas segundo o critério de Gini (Random Forest).](importancia_features_M7.png)  
**Figura 1 —** Ranking de importância relativa das características extraídas em janelas de $2,0\text{ s}$. **Fonte:** Elaborado pelo autor (2026).

**Quadro 1 — Contribuição percentual das principais características na discriminação entre Quedas e ADLs.**

| Posição | Característica | Símbolo Matemático | Importância Relativa (%) | Interpretação Física e Biomecânica |
| :---: | :--- | :---: | :---: | :--- |
| **1º** | `SVM_Max` | $\max(s_i)$ | $15,22\%$ | Intensidade máxima da desaceleração no choque com o solo |
| **2º** | `SVM_PtP` | $\text{SVM}_{\max} - \text{SVM}_{\min}$ | $13,87\%$ | Excursão total entre o alívio de queda livre e o pico de colisão |
| **3º** | `SVM_Skew` | $\gamma_1$ | $12,89\%$ | Assimetria impulsiva causada pelo pico isolado seguido de repouso |
| **4º** | `SVM_Kurt` | $\gamma_2$ | $8,81\%$ | Concentração leptocúrtica da onda de choque na janela de $2,0\text{ s}$ |
| **5º** | `SVM_Var` / `SVM_Std` | $\sigma^2_{\text{SVM}}, \sigma_{\text{SVM}}$ | $15,03\%$ (soma) | Energia de dispersão global do evento transitório |
| **6º** | Variâncias e Desvios Triaxiais | $\sigma^2_Z, \sigma^2_X, \sigma_Z, \sigma_X, \sigma^2_Y, \sigma_Y$ | $31,79\%$ (soma) | Mudança de orientação postural do tronco em relação à gravidade |

**Fonte:** Dados da pesquisa (2026).

Os resultados do Quadro 1 confirmam por que o limiar fixo isolado falha e o modelo supervisionado obtém êxito: embora `SVM_Max` responda por $15,22\%$ da decisão, **mais de $84\%$ do poder discriminativo provém da combinação de descritores morfológicos** (`SVM_PtP`, `SVM_Skew`, `SVM_Kurt`) e **posturais triaxiais** (variâncias nos eixos X, Y e Z), os quais diferenciam um impacto seguido de queda no chão de um salto ou corrida em que o indivíduo permanece em pé.

---

## REFERÊNCIAS

BOURKE, A. K.; O'BRIEN, J. V.; LYONS, G. M. Evaluation of a threshold-based tri-axial accelerometer fall detection algorithm. **Gait & Posture**, v. 26, n. 2, p. 194-199, 2007.

IGUAL, R.; MEDRANO, C.; PLAZA, I. Challenges, issues and trends in fall detection systems. **BioMedical Engineering OnLine**, v. 12, n. 1, p. 66, 2013.

PEDREGOSA, F. *et al.* Scikit-learn: Machine Learning in Python. **Journal of Machine Learning Research**, v. 12, p. 2825-2830, 2011.

SUCERQUIA, A.; LÓPEZ, J. D.; VARGAS-BONILLA, J. F. SisFall: A Fall and Movement Dataset. **Sensors**, v. 17, n. 1, p. 198, 2017.
