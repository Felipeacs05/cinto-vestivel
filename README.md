# UNIVERSIDADE ESTADUAL DE FEIRA DE SANTANA (UEFS)
**Pró-Reitoria de Pesquisa e Pós-Graduação (PPPG)**  
**Programa Institucional de Bolsas de Iniciação em Desenvolvimento Tecnológico e Inovação (PIBITI/CNPq)**  
**Edital PPPG-IT/UEFS Nº 02/2026**

# CINTO VESTÍVEL COM IOT PARA MONITORAMENTO DE IDOSOS

**Projeto de Pesquisa:** Sistemas Embarcados, Internet das Coisas (IoT) e Inteligência Artificial Aplicada à Saúde Assistiva  
**Orientador:** Prof. Dr. Germano Pinto Guedes (`germano@uefs.br`)  
**Discente Bolsista:** Felipe Amorim do Carmo Silva (`felipedocarmo05@gmail.com`)  

---

## VISÃO GERAL DO PROJETO

Este repositório reúne os artefatos de hardware, *firmware* (C++/Arduino para ESP32), scripts de Processamento Digital de Sinais (DSP), rotinas de Aprendizado de Máquina (*Machine Learning* / *TinyML*) e relatórios técnicos parciais desenvolvidos no âmbito do projeto de Iniciação Tecnológica **"Cinto Vestível com IoT para Monitoramento de Idosos"**.

O objetivo central do projeto consiste em superar a fragilidade dos algoritmos heurísticos de limiar fixo ($3,0\text{ g}$) na detecção de quedas em idosos, integrando um protótipo vestível baseado no microcontrolador **ESP32** e no sensor inercial **MPU-9250** com transmissão em nuvem (**Firebase Realtime Database**) e modelos supervisionados (**SVM** e **Random Forest**) treinados e validados sobre bases de dados científicas públicas (**SisFall** e **UMAFall**).

---

## ESTRUTURA DE DIRETÓRIOS POR MÊS DE EXECUÇÃO (MÊS 01 AO MÊS 08)

A organização do repositório acompanha rigorosamente o Cronograma de Execução de 12 meses definido no Plano de Trabalho:

| Diretório | Período | Etapa do Cronograma | Principais Artefatos e Resultados |
| :---: | :---: | :--- | :--- |
| [**`Mes01/`**](Mes01/README.md) | 1º Mês | Revisão Bibliográfica e Especificação de Hardware | [`Mes01/README.md`](Mes01/README.md) — Fundamentação teórica (SisFall, UMAFall, TinyML) e dimensionamento do ESP32 + MPU-9250 + LiPo. |
| [**`Mes02/`**](Mes02/README.md) | 2º Mês | Montagem em Protoboard e Aquisição Inercial I2C | [`Mes02/sketch_sep21a.ino`](Mes02/sketch_sep21a.ino), [`Mes02/README.md`](Mes02/README.md) — Comunicação I2C (`GPIO 8/9`), calibração de *offset* e cálculo de $\text{SVM}$. |
| [**`Mes03/`**](Mes03/README.md) | 3º Mês | Conectividade Wi-Fi e Integração com Firebase RTDB | [`Mes03/firmware_wifi_firebase.ino`](Mes03/firmware_wifi_firebase.ino), [`Mes03/README.md`](Mes03/README.md) — Envio periódico não bloqueante para `Sensores/Inercial/SVM`. |
| [**`Mes04/`**](Mes04/README.md) | 4º Mês | Download, Estruturação e Análise Exploratória (SisFall) | [`Mes04/baixar_sisfall.py`](Mes04/baixar_sisfall.py), [`Mes04/analise_sisfall.py`](Mes04/analise_sisfall.py), gráficos [`D01_SA01`](Mes04/exploratoria_D01_SA01_R01.png), [`F01_SA01`](Mes04/exploratoria_F01_SA01_R01.png) e [`D01_SE01`](Mes04/exploratoria_D01_SE01_R01.png). |
| [**`Mes05/`**](Mes05/README.md) | 5º Mês | Filtro Digital Butterworth (4ª Ordem, 5 Hz) e Unificação | [`Mes05/filtro_mes5.py`](Mes05/filtro_mes5.py), [`Mes05/unificador_sisfall.py`](Mes05/unificador_sisfall.py), [`comparativo_butterworth_M5.png`](Mes05/comparativo_butterworth_M5.png) ($4.505\text{ ensaios}$, $15,85\text{ milhões}$ de amostras). |
| [**`Mes06/`**](Mes06/README.md) | 6º Mês | Validação Físico-Experimental de Bancada (ESP32 + MPU-9250) | [`Mes06/teste_bancada_firebase/`](Mes06/teste_bancada_firebase/), [`analise_bancada_mes6.py`](Mes06/analise_bancada_mes6.py), [`dados_esp32_completos.csv`](Mes06/dados_esp32_completos.csv), [`validacao_bancada_M6.png`](Mes06/validacao_bancada_M6.png) — Coleta empírica de $5.283$ amostras a $50\text{ Hz}$ em 24 lotes no Firebase RTDB e geração automática dos gráficos. |
| [**`Mes07/`**](Mes07/README.md) | 7º Mês | Extração de Características em Janelas e Treinamento ML | [`Mes07/treinamento_ml_mes7.py`](Mes07/treinamento_ml_mes7.py), [`Mes07/features_sisfall_janelas.csv`](Mes07/features_sisfall_janelas.csv), [`Mes07/importancia_features_M7.png`](Mes07/importancia_features_M7.png). |
| [**`Mes08/`**](Mes08/README.md) | 8º Mês | Validação Cruzada (10-Fold) e Seleção do Modelo TinyML | [`Mes08/validacao_kfold_mes8.py`](Mes08/validacao_kfold_mes8.py), [`Mes08/metricas_10fold_M8.csv`](Mes08/metricas_10fold_M8.csv), [`comparativo_modelos_ml_M7_M8.png`](Mes08/comparativo_modelos_ml_M7_M8.png), [`estabilidade_kfold_M8.png`](Mes08/estabilidade_kfold_M8.png). |

---

## SÍNTESE DA VALIDAÇÃO EXPERIMENTAL DE BANCADA DO HARDWARE (MÊS 06)

No ensaio físico do dispositivo vestível (ESP32 + MPU-9250), validou-se a cadeia completa de aquisição e telemetria através da coleta contínua de **$5.283$ amostras** a $50\text{ Hz}$ organizadas em 24 lotes no **Firebase Realtime Database** ($105,66\text{ s}$ de ensaio contínuo):

| Regime Cinemático Avaliado | Intervalo ($t$) | Amostras ($N$) | $\text{SVM}_{\text{médio}} \pm \sigma$ | Mínimo | Máximo | Comportamento Observado |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Linha de Base Estática** | $0,0\text{ s} - 26,6\text{ s}$ | $1.330$ | $1,063 \pm 0,004\text{ g}$ | $1,048\text{ g}$ | $1,080\text{ g}$ | Repouso em bancada; ruído térmico reduzido ($\sigma = 0,004\text{ g}$). |
| **2. Oscilação Suave (Caminhada)** | $26,6\text{ s} - 53,0\text{ s}$ | $1.320$ | $1,081 \pm 0,165\text{ g}$ | $0,481\text{ g}$ | $1,944\text{ g}$ | Dinâmica de marcha normal; picos $< 2,0\text{ g}$ sem falsos alarmes. |
| **3. Movimentação Vigorosa (ADL)** | $53,0\text{ s} - 75,0\text{ s}$ | $1.100$ | $1,114 \pm 0,336\text{ g}$ | $0,266\text{ g}$ | $2,654\text{ g}$ | Excitação dinâmica intensa; picos contidos em $2,65\text{ g}$. |
| **4. Queda e Choques Agudos** | $75,0\text{ s} - 105,7\text{ s}$ | $1.533$ | $1,139 \pm 0,422\text{ g}$ | **$0,086\text{ g}$** | **$3,464\text{ g}$** | Vales de queda livre ($< 0,5\text{ g}$) seguidos de saturação em $3,464\text{ g}$. |

> [!NOTE]
> A saturação em exatamente $3,464\text{ g}$ decorre do limite de escala configurado no hardware ($\pm 2\text{ g}$ por eixo: $\sqrt{2^2 + 2^2 + 2^2} = \sqrt{12} \approx 3,4641\text{ g}$), comprovando experimentalmente a necessidade de fundos de escala maiores ($\pm 8\text{ g}$ ou $\pm 16\text{ g}$) implementados nas bases SisFall/UMAFall.

---

## SÍNTESE DOS RESULTADOS DE MACHINE LEARNING (SISFALL — MESES 07 E 08)

| Classificador Supervisionado | Acurácia (10-Fold) | Precisão | Recall (Sensibilidade) | F1-Score | Falsos Positivos (em 2.707 ADLs) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **SVM (Kernel RBF, $C=10$)** | **$99,71\%$** | **$99,89\%$** | **$99,39\%$** | **$99,64\%$** | $2$ ($0,07\%$) |
| **Random Forest ($100\text{ árvores}$)** | **$99,49\%$** | **$99,78\%$** | **$98,94\%$** | **$99,36\%$** | $4$ ($0,15\%$) |

---

## REFERÊNCIAS PRINCIPAIS

* BOURKE, A. K.; O'BRIEN, J. V.; LYONS, G. M. Evaluation of a threshold-based tri-axial accelerometer fall detection algorithm. **Gait & Posture**, v. 26, n. 2, p. 194-199, 2007.
* CASILARI, E.; SANTOYO-RAMÓN, J. A.; CANO-GARCÍA, J. M. UMAFall: A Multisensor Dataset for the Research on Automatic Fall Detection. **Procedia Computer Science**, v. 110, p. 32-39, 2017.
* OPPENHEIM, A. V.; SCHAFER, R. W. **Discrete-Time Signal Processing**. 3. ed. Upper Saddle River: Pearson, 2009.
* SUCERQUIA, A.; LÓPEZ, J. D.; VARGAS-BONILLA, J. F. SisFall: A Fall and Movement Dataset. **Sensors**, v. 17, n. 1, p. 198, 2017.
* WARDEN, P.; SITUNAYAKE, D. **TinyML**: Machine Learning with TensorFlow Lite on Arduino and Ultra-Low-Power Microcontrollers. Sebastopol: O'Reilly Media, 2019.
* WINTER, D. A. **Biomechanics and Motor Control of Human Movement**. 4. ed. Hoboken: John Wiley & Sons, 2009.
