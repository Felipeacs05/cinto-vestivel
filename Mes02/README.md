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

Uma vez que o cinto vestível está sujeito a variações de inclinação na cintura do usuário, avaliar um único eixo isolado tornaria o sistema dependente da orientação espacial do corpo no momento da queda. Para eliminar a dependência direcional no cálculo da intensidade do impacto, extrai-se o **Vetor de Soma da Magnitude** (*Signal Vector Magnitude* — $\text{SVM}$), definido pela norma euclidiana tridimensional (BOURKE; O'BRIEN; LYONS, 2007):

$$\text{SVM} = \sqrt{a_x^2 + a_y^2 + a_z^2}$$

Em condição de repouso estático (sem aceleração linear cinemática), a soma vetorial nos três eixos ortogonais reflete exclusivamente o campo gravitacional terrestre, de modo que $\text{SVM} \approx 1,000\text{ g}$ independentemente da rotação do sensor.

---

## 3 IMPLEMENTAÇÃO DO FIRMWARE DE AQUISIÇÃO E CALIBRAÇÃO

O código-fonte desenvolvido e validado nesta etapa encontra-se armazenado no arquivo [`sketch_sep21a.ino`](sketch_sep21a.ino). O firmware estrutura-se em três rotinas essenciais:

1. **Verificação de Identidade (`WHO_AM_I`):** Antes de iniciar a coleta, o microcontrolador requisita o conteúdo do registrador `0x75` (`WHO_AM_I_MPU9250`). A resposta hexadecimal `0x71` (específica do MPU-9250) ou `0x70` (variante compatível MPU-6500) valida a integridade da fiação I2C;
2. **Calibração de *Bias* em Repouso:** A função `mpu.calibrateMPU9250(mpu.gyroBias, mpu.accelBias)` acumula amostras com o sensor imóvel em superfície plana, estimando o desvio sistemático de fabricação (*zero-g offset*) e subtraindo-o nos registradores de compensação de hardware;
3. **Leitura Sincronizada por Interrupção (`INT_STATUS`):** No laço principal (`loop`), o barramento consulta o bit 0 (*Data Ready*) do registrador `INT_STATUS`, garantindo que a leitura dos registradores de aceleração ocorra somente quando uma nova conversão ADC estiver concluída.

### Listagem 1 — Firmware de Inicialização I2C, Calibração e Cálculo do SVM (`sketch_sep21a.ino`)

```cpp
#include <Wire.h>
#include "MPU9250.h"

MPU9250 mpu;

int sdaPin = 8;
int sclPin = 9;

void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println("\n--- INICIANDO MPU-9250 ---");
  Wire.begin(sdaPin, sclPin);
  delay(500);

  // Leitura do ID do sensor
  byte c = mpu.readByte(MPU9250_ADDRESS_AD0, WHO_AM_I_MPU9250);
  Serial.print("Sensor respondeu com ID: 0x");
  Serial.println(c, HEX);

  if (c == 0x71 || c == 0x70) {
    Serial.println("Sensor online e compativel!");
    
    // 1. Calibra o sensor
    Serial.println("Calibrando... Mantenha o sensor parado.");
    mpu.calibrateMPU9250(mpu.gyroBias, mpu.accelBias);

    // 2. Inicializa o sensor
    mpu.initMPU9250();
    Serial.println("Sensor inicializado com sucesso.");

    // 3. Define a resolucao/escala
    mpu.getAres();

  } else {
    Serial.println("Erro: Nao foi possivel comunicar com o MPU-9250.");
    Serial.println("Verifique as conexoes dos pinos VCC (3.3V), GND, SDA (GPIO 8) e SCL (GPIO 9).");
    while (1) { delay(100); }
  }
}

void loop() {
  if (mpu.readByte(MPU9250_ADDRESS_AD0, INT_STATUS) & 0x01) {
    mpu.readAccelData(mpu.accelCount);
    
    mpu.ax = (float)mpu.accelCount[0] * mpu.aRes;
    mpu.ay = (float)mpu.accelCount[1] * mpu.aRes;
    mpu.az = (float)mpu.accelCount[2] * mpu.aRes;

    // Cálculo do SVM (Signal Vector Magnitude)
    float svm = sqrt(sq(mpu.ax) + sq(mpu.ay) + sq(mpu.az));

    // Exibe o valor do SVM no Monitor Serial
    Serial.print("SVM: ");
    Serial.println(svm, 3);
  }
  
  delay(100);
}
```

---

## 4 RESULTADOS OBTIDOS EM BANCADA

Durante os ensaios de verificação via Monitor Serial a `115200 bps`, o sensor respondeu consistentemente com o identificador `0x71`. Após a execução da rotina `calibrateMPU9250()`, as leituras do vetor resultante $\text{SVM}$ com o protótipo em repouso sobre a bancada estabilizaram-se em $1,002\text{ g} \pm 0,008\text{ g}$, confirmando o correto alinhamento de escala e a eliminação de desvios sistemáticos estáticos.

---

## REFERÊNCIAS

BOURKE, A. K.; O'BRIEN, J. V.; LYONS, G. M. Evaluation of a threshold-based tri-axial accelerometer fall detection algorithm. **Gait & Posture**, v. 26, n. 2, p. 194-199, 2007.

ESPRESSIF SYSTEMS. **ESP32 Series Datasheet**. Xangai: Espressif Systems, 2026. Disponível em: https://docs.espressif.com. Acesso em: 20 ago. 2026.

INVENSENSE. **MPU-9250 Product Specification Revision 1.1**. San Jose: TDK InvenSense, 2026. Disponível em: https://invensense.tdk.com. Acesso em: 20 ago. 2026.
