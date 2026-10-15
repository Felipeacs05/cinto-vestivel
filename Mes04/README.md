# UNIVERSIDADE ESTADUAL DE FEIRA DE SANTANA (UEFS)
**Pró-Reitoria de Pesquisa e Pós-Graduação (PPPG)**  
**Programa Institucional de Bolsas de Iniciação em Desenvolvimento Tecnológico e Inovação (PIBITI/CNPq)**  
**Edital PPPG-IT/UEFS Nº 02/2026**

**Projeto de Pesquisa:** Sistemas Embarcados, Internet das Coisas (IoT) e Inteligência Artificial Aplicada à Saúde Assistiva  
**Plano de Trabalho:** Cinto Vestível com IoT para Monitoramento de Idosos  
**Orientador:** Prof. Dr. Germano Pinto Guedes (`germano@uefs.br`)  
**Bolsista:** Felipe Amorim do Carmo Silva (`felipedocarmo05@gmail.com`)  

---

# RELATÓRIO TÉCNICO PARCIAL — MÊS 04
**Período de Referência:** Mês 04 do Cronograma de Execução  
**Etapa:** Aquisição, Estruturação e Análise Exploratória do Dataset Público SisFall em Ambiente Python  
**Artefatos Associados:** [`baixar_sisfall.py`](baixar_sisfall.py), [`analise_sisfall.py`](analise_sisfall.py), [`exploratoria_D01_SA01_R01.png`](exploratoria_D01_SA01_R01.png), [`exploratoria_F01_SA01_R01.png`](exploratoria_F01_SA01_R01.png), [`exploratoria_D01_SE01_R01.png`](exploratoria_D01_SE01_R01.png)

---

## RESUMO

Este relatório apresenta o desenvolvimento e os resultados da etapa referente ao quarto mês de execução do projeto, dedicada à importação automatizada, tratamento inicial e análise exploratória da base de dados pública **SisFall** em ambiente Python. Os dados brutos do acelerômetro triaxial ADXL345 — originalmente expressos em unidades inteiras de conversão analógico-digital (ADC de 13 bits) — foram matematicamente convertidos para aceleração física em múltiplos da gravidade terrestre ($g$). Ademais, implementou-se um carregador híbrido tolerante a formato (capaz de processar tanto os arquivos `.txt` brutos originais quanto variantes `.csv` pré-processadas) e realizou-se o estudo comparativo de três cenários biomecânicos fundamentais: caminhada de adulto jovem (`D01_SA01`), queda frontal por escorregão (`F01_SA01`) e caminhada de voluntário idoso (`D01_SE01`).

**Palavras-chave:** Análise Exploratória de Dados. SisFall. Acelerometria Triaxial. Biomecânica da Queda. Python.

---

## 1 ESTRUTURA DA BASE DE DADOS SISFALL E RELEVÂNCIA METODOLÓGICA

A base de dados **SisFall** (SUCERQUIA; LÓPEZ; VARGAS-BONILLA, 2017) foi obtida programaticamente por meio da biblioteca `kagglehub` ([`baixar_sisfall.py`](baixar_sisfall.py)) e organizada localmente em subdiretórios correspondentes aos 38 voluntários participantes (`SA01` a `SA23` para adultos jovens de 19 a 30 anos; `SE01` a `SE15` para idosos de 60 a 75 anos), totalizando **4.505 arquivos** de séries temporais.

### 1.1 A Limitação Ética e a Prevenção de Falsos Positivos

Por restrições éticas e de segurança médica, os voluntários idosos (`SE`) não foram submetidos a simulações de queda em colchão, executando exclusivamente Atividades de Vida Diária (arquivos iniciados com o prefixo `D`, como caminhar, sentar-se e subir escadas), com a única exceção do participante `SE06`, especialista em judô (SUCERQUIA; LÓPEZ; VARGAS-BONILLA, 2017). Os voluntários jovens (`SA`), por sua vez, realizaram tanto as 19 atividades cotidianas (`D01` a `D19`) quanto as 15 categorias de quedas (`F01` a `F15`).

A fusão dessas duas coortes demográficas cumpre um papel determinante no treinamento do futuro classificador embarcado: caso o modelo fosse treinado somente com o grupo `SE`, jamais reconheceria a assinatura matemática de uma queda; inversamente, caso fosse treinado apenas com o grupo `SA`, sofreria perda de especificidade e sensibilidade ao monitorar um usuário idoso real, cujo padrão de marcha mais arrastado ou transição postural mais brusca ao sentar-se poderia ser confundido com um evento de queda.

### 1.2 Codificação dos Sensores, Taxa de Amostragem e Conversão ADC para Gravidade ($g$)

Cada arquivo bruto (`.txt`) do SisFall foi amostrado a uma taxa constante de $f_s = 200\text{ Hz}$ ($1\text{ s} = 200\text{ amostras}$) e contém 9 colunas separadas por vírgula, terminadas por ponto e vírgula (`;`):
* **Colunas 1, 2 e 3 (`ADXL_X`, `ADXL_Y`, `ADXL_Z`):** Acelerômetro triaxial **ADXL345**, configurado com resolução de $\text{Res} = 13\text{ bits}$ e fundo de escala de $\text{Range} = \pm 16\text{ g}$;
* **Colunas 4, 5 e 6 (`ITG_X`, `ITG_Y`, `ITG_Z`):** Giroscópio triaxial **ITG3200** ($\pm 2000^\circ/\text{s}$, 16 bits);
* **Colunas 7, 8 e 9 (`MMA_X`, `MMA_Y`, `MMA_Z`):** Acelerômetro secundário **MMA8451Q** ($\pm 8\text{ g}$, 14 bits).

Conforme especificado na documentação técnica oficial do SisFall, a conversão do valor digital bruto em bits ($\text{AD}$) do acelerômetro principal ADXL345 para unidades de aceleração da gravidade ($g$) obedece à equação:

$$a_{[g]} = \left( \frac{2 \times \text{Range}}{2^{\text{Resolution}}} \right) \times \text{AD} = \left( \frac{2 \times 16}{2^{13}} \right) \times \text{AD} = \frac{32}{8192} \times \text{AD} = \frac{\text{AD}}{256,0}$$

Portanto, cada incremento de $256\text{ LSB}$ (*Least Significant Bits*) equivale exatamente a $1,0\text{ g}$ ($9,80665\text{ m/s}^2$).

---

## 2 ENGENHARIA DE SOFTWARE: LEITURA HÍBRIDA (`.TXT` E `.CSV`)

Durante a manipulação da base de dados, verificou-se que repositórios secundários do SisFall disponibilizam versões convertidas em formato `.csv` contendo cabeçalho textual (`ADXL345_Acc_X`, `ADXL345_Acc_Y`, `ADXL345_Acc_Z`, ..., `FallCheck`) cujas amostras já se encontram pré-divididas por $256,0$. Caso um script projetado estritamente para `.txt` tentasse abrir um ambiente contendo arquivos `.csv`, ocorreria falha de execução (`FileNotFoundError`) ou dupla divisão por $256,0$.

Para assegurar robustez e reprodutibilidade ao projeto, implementou-se no script [`analise_sisfall.py`](analise_sisfall.py) a função `carregar_arquivo_sisfall()`, que inspeciona automaticamente a extensão e a estrutura das colunas do arquivo, aplicando a conversão $\text{AD}/256,0$ exclusivamente sobre matrizes brutas em bits.

### Listagem 1 — Script de Análise Exploratória e Plotagem Inercial (`analise_sisfall.py`)

```python
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def carregar_arquivo_sisfall(caminho_arquivo):
    # Alterna automaticamente entre .txt e .csv caso um deles não exista no caminho informado
    if not os.path.exists(caminho_arquivo):
        base, ext = os.path.splitext(caminho_arquivo)
        alternativo = base + ('.csv' if ext.lower() == '.txt' else '.txt')
        if os.path.exists(alternativo):
            caminho_arquivo = alternativo
        else:
            raise FileNotFoundError(f"Arquivo não encontrado (.txt ou .csv): {caminho_arquivo}")
