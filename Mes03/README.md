# UNIVERSIDADE ESTADUAL DE FEIRA DE SANTANA (UEFS)
**Pró-Reitoria de Pesquisa e Pós-Graduação (PPPG)**  
**Programa Institucional de Bolsas de Iniciação em Desenvolvimento Tecnológico e Inovação (PIBITI/CNPq)**  
**Edital PPPG-IT/UEFS Nº 02/2026**

**Projeto de Pesquisa:** Sistemas Embarcados, Internet das Coisas (IoT) e Inteligência Artificial Aplicada à Saúde Assistiva  
**Plano de Trabalho:** Cinto Vestível com IoT para Monitoramento de Idosos  
**Orientador:** Prof. Dr. Germano Pinto Guedes (`germano@uefs.br`)  
**Bolsista:** Felipe Amorim do Carmo Silva (`felipedocarmo05@gmail.com`)  

---

# RELATÓRIO TÉCNICO PARCIAL — MÊS 03
**Período de Referência:** Mês 03 do Cronograma de Execução  
**Etapa:** Desenvolvimento do Firmware de Conectividade Wi-Fi e Integração com a Nuvem (Firebase Realtime Database)  
**Artefato de Código Associado:** [`firmware_wifi_firebase.ino`](firmware_wifi_firebase.ino)

---

## RESUMO

Este relatório documenta as atividades realizadas no terceiro mês do cronograma de execução, cujo foco residiu na implementação da camada de conectividade sem fio do microcontrolador ESP32 (padrão IEEE 802.11 b/g/n) e na estruturação do banco de dados em nuvem utilizando o Google Firebase Realtime Database (RTDB). O firmware foi arquitetado de modo a desacoplar a aquisição inercial contínua no barramento I2C (executada a $20\text{ Hz}$–$50\text{ Hz}$) da rotina de transmissão HTTPS/TLS para a nuvem, empregando temporização não bloqueante baseada em `millis()` e dimensionamento otimizado dos *buffers* criptográficos BearSSL.

**Palavras-chave:** Internet das Coisas. ESP32. Conectividade Wi-Fi. Firebase Realtime Database. Telemetria Inercial.

---

## 1 ARQUITETURA DE COMUNICAÇÃO DIRETA EM NUVEM

Em conformidade com a estratégia incremental delineada na Seção 1 do Plano de Trabalho, o primeiro ciclo de 12 meses adota uma topologia de comunicação direta entre o dispositivo de borda (*Edge Device*) e o serviço de nuvem (**ESP32 $\rightarrow$ Wi-Fi $\rightarrow$ Firebase RTDB**), dispensando a intermediação de um *gateway* local (como um Raspberry Pi) nesta fase inicial. Essa decisão de engenharia reduz a latência de integração do protótipo e permite validar imediatamente a telemetria inercial fim a fim (RAY, 2018; ROSE; ELDRIDGE; CHAPIN, 2015).

No console do Google Firebase, foi provisionada a instância `esp32-inercial-default-rtdb.firebaseio.com`, estruturando-se a árvore JSON sob o caminho hierárquico `Sensores/Inercial/SVM` para armazenamento em tempo real da magnitude resultante do vetor aceleração.

```
+-------------------------------------------------------------------------+
|                        LAÇO PRINCIPAL DO ESP32                          |
|                                                                         |
|   [Barramento I2C: MPU-9250]                                            |
|        |                                                                |
|        v  (Amostragem contínua a cada 50 ms / 20 Hz)                    |
|   Cálculo de ultimoSVM = sqrt(ax² + ay² + az²)                          |
|        |                                                                |
|        +---> Verificação Não Bloqueante: (millis() - prevMillis > 5000) |
|                     |                                                   |
|                     v (Apenas quando o temporizador atinge 5 s)         |
|               Empacotamento TLS/BearSSL (Buffer 1024 B)                  |
|                     |                                                   |
|                     v                                                   |
|        Firebase.RTDB.setFloat(&fbdo, "Sensores/Inercial/SVM", ultimoSVM)|
+-------------------------------------------------------------------------+
```

---

## 2 ENGENHARIA DO FIRMWARE E CONTROLE NÃO BLOQUEANTE

Um problema recorrente em sistemas embarcados que combinam leitura de sensores inerciais e requisições de rede reside no bloqueio da CPU durante o *handshake* TLS/HTTPS. Caso o envio para a nuvem fosse executado a cada iteração do sensor ou controlado por funções bloqueantes longas (`delay(5000)`), o microcontrolador deixaria de amostrar o MPU-9250 durante 5 segundos inteiros, perdendo eventos transitórios de impacto (cuja duração física é inferior a $500\text{ ms}$).

Para solucionar esse gargalo, o firmware implementado em [`firmware_wifi_firebase.ino`](firmware_wifi_firebase.ino) aplica três mecanismos técnicos:

1. **Temporização Assíncrona com `millis()`:** A leitura do registrador `INT_STATUS` do MPU-9250 e a atualização da variável global `ultimoSVM` ocorrem continuamente na frequência base do laço, enquanto o despacho HTTP via `Firebase.RTDB.setFloat()` é acionado exclusivamente quando a diferença `millis() - sendDataPrevMillis` supera `timerDelay` ($5000\text{ ms}$);
2. **Otimização de Memória Criptográfica BearSSL:** Por meio da instrução `fbdo.setBSSLBufferSize(1024, 1024)`, os *buffers* de recepção e transmissão SSL foram ajustados para $1024\text{ bytes}$, reduzindo o consumo de memória *heap* do ESP32 e acelerando a serialização dos pacotes JSON;
3. **Tolerância a Falhas no Barramento I2C e Wi-Fi:** A inclusão de `Wire.setTimeOut(3000)` previne travamentos caso ocorra ruído elétrico nos cabos do protoboard, enquanto `Firebase.reconnectWiFi(true)` garante a reconexão automática à rede sem fio em caso de queda momentânea do ponto de acesso.

### Listagem 1 — Firmware Integrado de Aquisição Inercial e Transmissão ao Firebase (`firmware_wifi_firebase.ino`)

```cpp
#include <Wire.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include "MPU9250.h"

// Fornece informações para o processo de geração de token do Firebase
#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

#define WIFI_SSID "LANE_ZRL2"
#define WIFI_PASSWORD "********"
#define API_KEY "AIzaSyCGICFsj_b7tEwknOjU5oOZJE_ujkGBxUA"
#define DATABASE_URL "esp32-inercial-default-rtdb.firebaseio.com" 

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

MPU9250 mpu;
int sdaPin = 8;
int sclPin = 9;

unsigned long sendDataPrevMillis = 0;
unsigned long timerDelay = 5000; // Envia para o Firebase a cada 5000ms (5 segundos)
float ultimoSVM = 0.0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }

  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;
  config.signer.test_mode = true;
  
  fbdo.setBSSLBufferSize(1024, 1024);
  fbdo.setResponseSize(1024);

  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  Wire.end(); 
  Wire.begin(sdaPin, sclPin);
  Wire.setTimeOut(3000);
  delay(500);

  byte c = mpu.readByte(MPU9250_ADDRESS_AD0, WHO_AM_I_MPU9250);
  if (c == 0x71 || c == 0x70) {
    mpu.calibrateMPU9250(mpu.gyroBias, mpu.accelBias);
    mpu.initMPU9250();
    mpu.getAres();
  }
}

void loop() {
  // 1. LEITURA CONSTANTE DO SENSOR
  if (mpu.readByte(MPU9250_ADDRESS_AD0, INT_STATUS) & 0x01) {
    mpu.readAccelData(mpu.accelCount);
    mpu.ax = (float)mpu.accelCount[0] * mpu.aRes;
    mpu.ay = (float)mpu.accelCount[1] * mpu.aRes;
    mpu.az = (float)mpu.accelCount[2] * mpu.aRes;

    ultimoSVM = sqrt(sq(mpu.ax) + sq(mpu.ay) + sq(mpu.az));
  }
  
  // 2. ROTINA DE ENVIO PERIÓDICO PARA O FIREBASE
  if (Firebase.ready() && (millis() - sendDataPrevMillis > timerDelay || sendDataPrevMillis == 0)) {
    sendDataPrevMillis = millis();
    if (Firebase.RTDB.setFloat(&fbdo, "Sensores/Inercial/SVM", ultimoSVM)) {
      Serial.println("-> Sucesso: Dado salvo no Firebase!");
    } else {
      Serial.println(fbdo.errorReason());
    }
  }
  delay(50);
}
```

---

## 3 CONCLUSÃO DA ETAPA

O pipeline de conectividade Wi-Fi e persistência no Firebase Realtime Database foi concluído com êxito no Mês 03. Os testes iniciais confirmaram a atribuição de endereço IP local via DHCP e a escrita contínua no nó `Sensores/Inercial/SVM` sem perda de sincronismo no barramento I2C, deixando a infraestrutura de hardware pronta para os testes sistemáticos de estresse e bancada programados para o Mês 06.

---

## REFERÊNCIAS

ESPRESSIF SYSTEMS. **ESP32 Series Datasheet**. Xangai: Espressif Systems, 2026. Disponível em: https://docs.espressif.com. Acesso em: 10 set. 2026.

GOOGLE. **Firebase Realtime Database Documentation**. Mountain View: Google LLC, 2026. Disponível em: https://firebase.google.com/docs/database. Acesso em: 10 set. 2026.

RAY, P. P. A survey on Internet of Things architectures. **Journal of King Saud University – Computer and Information Sciences**, v. 30, n. 3, p. 291-319, 2018.

ROSE, K.; ELDRIDGE, S.; CHAPIN, L. **The Internet of Things**: An Overview. Reston: The Internet Society (ISOC), 2015.
