# UNIVERSIDADE ESTADUAL DE FEIRA DE SANTANA (UEFS)
**Pró-Reitoria de Pesquisa e Pós-Graduação (PPPG)**  
**Programa Institucional de Bolsas de Iniciação em Desenvolvimento Tecnológico e Inovação (PIBITI/CNPq)**  
**Edital PPPG-IT/UEFS Nº 02/2026**

**Projeto de Pesquisa:** Sistemas Embarcados, Internet das Coisas (IoT) e Inteligência Artificial Aplicada à Saúde Assistiva  
**Plano de Trabalho:** Cinto Vestível com IoT para Monitoramento de Idosos  
**Orientador:** Prof. Dr. Germano Pinto Guedes (`germano@uefs.br`)  
**Bolsista:** Felipe Amorim do Carmo Silva (`felipedocarmo05@gmail.com`)  

---

# RELATÓRIO TÉCNICO PARCIAL — MÊS 02
**Período de Referência:** Mês 02 do Cronograma de Execução  
**Etapa:** Montagem do Circuito Físico em Protoboard, Aquisição Inercial I2C e Calibração do Sensor MPU-9250  
**Artefato de Código Associado:** [`sketch_sep21a.ino`](sketch_sep21a.ino)

---

## RESUMO

Este relatório descreve as atividades desenvolvidas durante o segundo mês de vigência do plano de trabalho, compreendendo a integração física do microcontrolador ESP32 com a unidade de medição inercial (IMU) MPU-9250 em matriz de contatos (*protoboard*), a implementação do protocolo de comunicação síncrona I2C e o desenvolvimento do firmware básico de calibração de *offset* e cálculo da Magnitude do Vetor de Sinal (*Signal Vector Magnitude* — SVM). A verificação de identidade do dispositivo por meio do registrador `WHO_AM_I` (`0x75`) confirmou a integridade elétrica do barramento, enquanto a rotina de calibração estática assegurou a convergência das leituras basais para o referencial gravitacional terrestre ($1,0\text{ g}$).

**Palavras-chave:** ESP32. MPU-9250. Barramento I2C. Calibração Inercial. Vetor de Soma da Magnitude.

---

## 1 MONTAGEM FÍSICA E INTEGRAÇÃO DO BARRAMENTO I2C

A primeira atividade prática do Mês 02 consistiu na interconexão elétrica entre o microcontrolador ESP32 e o módulo sensor MPU-9250 em bancada. O MPU-9250 integra em um único encapsulamento *System in Package* (SiP) dois circuitos integrados distintos: o chip principal **MPU-6500** (contendo o acelerômetro triaxial e o giroscópio triaxial) e o magnetômetro **AK8963** (INVENSENSE, 2026).

Para estabelecer comunicação digital síncrona com baixa ocupação de pinos, adotou-se o barramento **I2C** (*Inter-Integrated Circuit*), utilizando o pino `GPIO 8` para a linha de dados bidirecional (`SDA`) e o pino `GPIO 9` para o sinal de *clock* (`SCL`). O pino `AD0` do módulo sensor foi mantido em nível lógico baixo (`GND`), fixando o endereço escravo de 7 bits do dispositivo em `0x68`.

**Quadro 1 — Mapeamento de pinagem entre o microcontrolador ESP32 e o módulo inercial MPU-9250.**

| Pino no Módulo MPU-9250 | Pino no Microcontrolador ESP32 | Função Elétrica e Lógica |
| :--- | :--- | :--- |
| **VCC** | `3V3` ($3,3\text{ V}$) | Alimentação regulada para os conversores internos e sistemas MEMS |
| **GND** | `GND` ($0,0\text{ V}$) | Referencial comum de terra do circuito |
| **SDA** | `GPIO 8` | Linha serial de dados (*Serial Data*) do barramento I2C |
| **SCL** | `GPIO 9` | Linha serial de *clock* (*Serial Clock*) do barramento I2C |
| **AD0** | `GND` (Interno/Pull-down) | Seleção do bit menos significativo do endereço I2C (`0x68`) |

**Fonte:** Elaborado pelo autor (2026).

---

## 2 FUNDAMENTAÇÃO MATEMÁTICA DA CONVERSÃO E DO VETOR SVM

Os sinais mecânicos captados pelas estruturas microeletromecânicas (MEMS) do MPU-9250 são digitalizados por conversores analógico-digitais (ADC) internos de 16 bits em complemento de dois, gerando valores inteiros brutos no intervalo $[-32768, +32767]$. Para converter a leitura digital bruta de cada eixo ($C_x, C_y, C_z$) em unidades físicas de aceleração da gravidade ($g$, onde $1,0\text{ g} \approx 9,80665\text{ m/s}^2$), aplica-se o fator de resolução escalar $a_{\text{Res}}$:

$$a_k = C_k \cdot a_{\text{Res}}, \quad \text{para } k \in \{x, y, z\}$$

Considerando o fundo de escala padrão inicial de $\pm 2\text{ g}$, a sensibilidade nominal é de $16384\text{ LSB/g}$, o que resulta em $a_{\text{Res}} = \frac{2,0}{32768} \approx 0,000061035\text{ g/LSB}$.

