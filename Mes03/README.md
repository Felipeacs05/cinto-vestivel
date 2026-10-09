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

