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

A organização do repositório acompanha rigorosamente o Cronograma de Execução de 12 meses definido no Plano de Trabalho, encontrando-se consolidada até o **Mês 08**:

| Diretório | Período | Etapa do Cronograma | Principais Artefatos e Resultados |
| :---: | :---: | :--- | :--- |
| [**`Mes01/`**](Mes01/README.md) | 1º Mês | Revisão Bibliográfica e Especificação de Hardware | [`Mes01/README.md`](Mes01/README.md) — Fundamentação teórica (SisFall, UMAFall, TinyML) e dimensionamento do ESP32 + MPU-9250 + LiPo. |
| [**`Mes02/`**](Mes02/README.md) | 2º Mês | Montagem em Protoboard e Aquisição Inercial I2C | [`Mes02/sketch_sep21a.ino`](Mes02/sketch_sep21a.ino), [`Mes02/README.md`](Mes02/README.md) — Comunicação I2C (`GPIO 8/9`), calibração de *offset* e cálculo de $\text{SVM}$. |
| [**`Mes03/`**](Mes03/README.md) | 3º Mês | Conectividade Wi-Fi e Integração com Firebase RTDB | [`Mes03/firmware_wifi_firebase.ino`](Mes03/firmware_wifi_firebase.ino), [`Mes03/README.md`](Mes03/README.md) — Envio periódico não bloqueante para `Sensores/Inercial/SVM`. |
| [**`Mes04/`**](Mes04/README.md) | 4º Mês | Download, Estruturação e Análise Exploratória (SisFall) | [`Mes04/baixar_sisfall.py`](Mes04/baixar_sisfall.py), [`Mes04/analise_sisfall.py`](Mes04/analise_sisfall.py), gráficos [`D01_SA01`](Mes04/exploratoria_D01_SA01_R01.png), [`F01_SA01`](Mes04/exploratoria_F01_SA01_R01.png) e [`D01_SE01`](Mes04/exploratoria_D01_SE01_R01.png). |
| [**`Mes05/`**](Mes05/README.md) | 5º Mês | Filtro Digital Butterworth (4ª Ordem, 5 Hz) e Unificação | [`Mes05/filtro_mes5.py`](Mes05/filtro_mes5.py), [`Mes05/unificador_sisfall.py`](Mes05/unificador_sisfall.py), [`comparativo_butterworth_M5.png`](Mes05/comparativo_butterworth_M5.png) ($4.505\text{ ensaios}$, $15,85\text{ milhões}$ de amostras). |
| [**`Mes06/`**](Mes06/README.md) | 6º Mês | Testes de Bancada do Hardware e Telemetria de Picos | [`Mes06/teste_bancada_firebase.ino`](Mes06/teste_bancada_firebase.ino), [`Mes06/validacao_bancada_M6.png`](Mes06/validacao_bancada_M6.png), [`Mes06/README.md`](Mes06/README.md). |
| [**`Mes07/`**](Mes07/README.md) | 7º Mês | Extração de Características em Janelas e Treinamento ML | [`Mes07/treinamento_ml_mes7.py`](Mes07/treinamento_ml_mes7.py), [`Mes07/features_sisfall_janelas.csv`](Mes07/features_sisfall_janelas.csv), [`Mes07/importancia_features_M7.png`](Mes07/importancia_features_M7.png). |
| [**`Mes08/`**](Mes08/README.md) | 8º Mês | Validação Cruzada (10-Fold) e Seleção do Modelo TinyML | [`Mes08/validacao_kfold_mes8.py`](Mes08/validacao_kfold_mes8.py), [`Mes08/metricas_10fold_M8.csv`](Mes08/metricas_10fold_M8.csv), [`comparativo_modelos_ml_M7_M8.png`](Mes08/comparativo_modelos_ml_M7_M8.png), [`estabilidade_kfold_M8.png`](Mes08/estabilidade_kfold_M8.png). |

---

