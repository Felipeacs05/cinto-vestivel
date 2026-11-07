# UNIVERSIDADE ESTADUAL DE FEIRA DE SANTANA (UEFS)
**Pró-Reitoria de Pesquisa e Pós-Graduação (PPPG)**  
**Programa Institucional de Bolsas de Iniciação em Desenvolvimento Tecnológico e Inovação (PIBITI/CNPq)**  
**Edital PPPG-IT/UEFS Nº 02/2026**

**Projeto de Pesquisa:** Sistemas Embarcados, Internet das Coisas (IoT) e Inteligência Artificial Aplicada à Saúde Assistiva  
**Plano de Trabalho:** Cinto Vestível com IoT para Monitoramento de Idosos  
**Orientador:** Prof. Dr. Germano Pinto Guedes (`germano@uefs.br`)  
**Bolsista:** Felipe Amorim do Carmo Silva (`felipedocarmo05@gmail.com`)  

---

# RELATÓRIO TÉCNICO PARCIAL — MÊS 06
**Período de Referência:** Mês 06 do Cronograma de Execução  
**Etapa:** Preparação e Protocolo para Testes de Bancada do Hardware (ESP32 + MPU-9250) com Detector de Pico Digital e Integrador Temporal  
**Artefato Associado:** [`teste_bancada_firebase.ino`](teste_bancada_firebase.ino)

---

## RESUMO

Este documento descreve a preparação de engenharia, a instrumentação de *firmware* e o protocolo experimental referentes ao sexto mês do cronograma de execução, destinado aos testes físicos de bancada do protótipo (ESP32 + MPU-9250) para validação da comunicação sem fio e do envio de picos inerciais ao Google Firebase Realtime Database. A fim de garantir que impactos transitórios rápidos (cuja duração física situa-se entre $10\text{ ms}$ e $50\text{ ms}$) não sejam perdidos no intervalo entre envios de rede ($5.000\text{ ms}$), implementou-se no *firmware* [`teste_bancada_firebase.ino`](teste_bancada_firebase.ino) uma arquitetura combinada de amostragem a $50\text{ Hz}$ com **Detector de Pico Digital (*Peak-Hold*)** e **Integrador Discreto de Janela (Média Móvel Acumulada)**, além do filtro passa-baixa digital interno (DLPF) do conversor ADC Sigma-Delta de 16 bits do MPU-9250.

**Palavras-chave:** Validação de Bancada. Detector de Pico Digital. Circuito Integrador Discreto. ESP32. Firebase RTDB.

---

## 1 FUNDAMENTAÇÃO DE INSTRUMENTAÇÃO: DETECÇÃO E RETENÇÃO DE PICOS INERCIAIS

Um evento de impacto mecânico caracteriza-se por um pulso estreito de alta amplitude no domínio do tempo. Quando o sistema de transmissão para a nuvem opera em intervalos periódicos (ex.: a cada $5\text{ segundos}$ para evitar bloqueio da CPU pelo *handshake* TLS/HTTPS), a simples transmissão da última leitura instantânea (`ultimoSVM`) ocasionaria a perda de picos ocorridos no interior da janela entre envios.

Para solucionar esse problema clássico de instrumentação eletrônica, o subsistema desenvolvido no Mês 06 atua em três camadas complementares:

1. **Conversão ADC Rápida e Filtragem Integradora em Hardware (MPU-9250):** Os conversores analógico-digitais Sigma-Delta de 16 bits internos do MPU-9250 amostram as estruturas MEMS em alta velocidade ($1\text{ kHz}$) e submetem o sinal ao *Digital Low-Pass Filter* (DLPF) interno do chip (INVENSENSE, 2026). Fisicamente, o DLPF opera como um **circuito integrador passa-baixa**, suavizando ruídos térmicos e alargando temporalmente os pulsos de impacto antes da leitura via barramento I2C;
2. **Detector de Pico Digital (*Software Peak-Hold*) no ESP32:** O microcontrolador consulta o sensor a uma taxa de $50\text{ Hz}$ (a cada $20\text{ ms}$, conforme estipulado na Etapa 2 de Materiais e Métodos do Plano de Trabalho). A cada amostra $s_k$, o algoritmo retém em memória o valor máximo (`picoMaximoSVM`) e o valor mínimo de queda livre (`valeMinimoSVM`) registrados desde o último envio à nuvem:
   $$\text{SVM}_{\text{Pico}} = \max_{1 \le k \le M} (s_k), \quad \text{SVM}_{\text{Vale}} = \min_{1 \le k \le M} (s_k)$$
3. **Integrador Numérico na Janela Temporal:** Simultaneamente, acumula-se a soma discreta das $M$ amostras colhidas na janela para extrair a energia média integrada do período ($\overline{\text{SVM}} = \frac{1}{M}\sum_{k=1}^{M} s_k$). Ao término do temporizador de $5\text{ s}$, o pacote JSON completo é despachado ao Firebase e os registradores de retenção são reiniciados para o ciclo seguinte.

---

## 2 FIRMWARE DE TESTE DE BANCADA (`teste_bancada_firebase.ino`)

A Listagem 1 apresenta o núcleo do código-fonte preparado em [`teste_bancada_firebase.ino`](teste_bancada_firebase.ino) para execução dos ensaios físicos de bancada.

### Listagem 1 — Rotina de Amostragem a 50 Hz com Detector de Pico (*Peak-Hold*) e Integrador (`teste_bancada_firebase.ino`)

```cpp
void loop() {
  // 1. AMOSTRAGEM RÁPIDA (50 Hz / a cada 20 ms) COM DETECTOR DE PICO E INTEGRADOR
  if (mpu.readByte(MPU9250_ADDRESS_AD0, INT_STATUS) & 0x01) {
    mpu.readAccelData(mpu.accelCount);
    
    mpu.ax = (float)mpu.accelCount[0] * mpu.aRes;
    mpu.ay = (float)mpu.accelCount[1] * mpu.aRes;
    mpu.az = (float)mpu.accelCount[2] * mpu.aRes;

    ultimoSVM = sqrt(sq(mpu.ax) + sq(mpu.ay) + sq(mpu.az));

    // Detector de Pico Digital (Peak-Hold): retém o maior impacto ocorrido na janela
    if (ultimoSVM > picoMaximoSVM) {
      picoMaximoSVM = ultimoSVM;
    }
    // Detector de Vale (Queda Livre): retém o menor valor ocorrido na janela
    if (ultimoSVM < valeMinimoSVM) {
      valeMinimoSVM = ultimoSVM;
    }
    // Acumulador Integrador para cálculo da média da janela
    somaIntegradoraSVM += ultimoSVM;
    contadorAmostras++;
  }
  
  // 2. ROTINA DE ENVIO PERIÓDICO PARA O FIREBASE (Descarrega o Pico Retido e reinicia a janela)
  if (Firebase.ready() && (millis() - sendDataPrevMillis > timerDelay || sendDataPrevMillis == 0)) {
    sendDataPrevMillis = millis();

    float mediaIntegradaSVM = (contadorAmostras > 0) ? (somaIntegradoraSVM / contadorAmostras) : ultimoSVM;
    float picoParaEnvio = (contadorAmostras > 0) ? picoMaximoSVM : ultimoSVM;

    FirebaseJson json;
    json.set("SVM_Instantaneo", ultimoSVM);
    json.set("SVM_Pico_Janela", picoParaEnvio);
    json.set("SVM_Media_Integrada", mediaIntegradaSVM);
    json.set("SVM_Vale_Minimo", (contadorAmostras > 0) ? valeMinimoSVM : ultimoSVM);
    json.set("Amostras_Janela", contadorAmostras);

    Firebase.RTDB.setJSON(&fbdo, "Sensores/Inercial", &json);

    // Reinicia o Detector de Pico e o Integrador para a próxima janela
    picoMaximoSVM = 0.0;
    valeMinimoSVM = 99.0;
    somaIntegradoraSVM = 0.0;
    contadorAmostras = 0;
  }
  delay(20); // 50 Hz
}
```

---

## 3 PROTOCOLO DE EXECUÇÃO E EXPORTAÇÃO DE DADOS DO FIREBASE

Conforme definido na Seção 4 do Plano de Trabalho, os testes de bancada do Mês 06 destinam-se exclusivamente à validação sistêmica do hardware físico e da comunicação com a nuvem (enquanto o treinamento dos algoritmos de Machine Learning nos Meses 07 e 08 utiliza integralmente os datasets científicos públicos SisFall/UMAFall).

**Quadro 1 — Roteiro de ensaio em bancada para coleta e exportação no Firebase RTDB.**

| Etapa do Ensaio | Procedimento Mecânico Manual | Variável Alvo no Firebase (`Sensores/Inercial`) | Critério de Aceitação |
| :--- | :--- | :--- | :--- |
| **1. Linha de Base Estática** | Manter a protoboard em repouso sobre a bancada por $15\text{ s}$ | `SVM_Media_Integrada` e `SVM_Pico_Janela` | Convergência em $1,00\text{ g} \pm 0,05\text{ g}$ |
| **2. Agitação Oscilatória** | Movimentar manualmente o sensor em ciclos suaves ($1\text{ Hz}$ a $2\text{ Hz}$) | `SVM_Media_Integrada` e `SVM_Pico_Janela` | Picos moderados entre $1,2\text{ g}$ e $2,0\text{ g}$ sem erro I2C |
| **3. Simulação de Impacto Agudo** | Movimentação vigorosa rápida seguida de parada brusca sobre anteparo macio | `SVM_Pico_Janela` e `SVM_Vale_Minimo` | Retenção de pico $> 3,0\text{ g}$ e confirmação `HTTP 200` no Firebase |
| **4. Exportação do Log** | Exportar o nó JSON do Firebase RTDB após os testes de bancada | Arquivo `.json` / `.csv` do ensaio | Anexação dos dados reais coletados na pasta `Mes06/` |

**Fonte:** Elaborado pelo autor (2026).

---

## REFERÊNCIAS

BOURKE, A. K.; O'BRIEN, J. V.; LYONS, G. M. Evaluation of a threshold-based tri-axial accelerometer fall detection algorithm. **Gait & Posture**, v. 26, n. 2, p. 194-199, 2007.

ESPRESSIF SYSTEMS. **ESP32 Series Datasheet**. Xangai: Espressif Systems, 2026. Disponível em: https://docs.espressif.com. Acesso em: 20 out. 2026.

GOOGLE. **Firebase Realtime Database Documentation**. Mountain View: Google LLC, 2026. Disponível em: https://firebase.google.com/docs/database. Acesso em: 20 out. 2026.

INVENSENSE. **MPU-9250 Product Specification Revision 1.1**. San Jose: TDK InvenSense, 2026. Disponível em: https://invensense.tdk.com. Acesso em: 20 out. 2026.
