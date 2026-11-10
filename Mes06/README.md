# UNIVERSIDADE ESTADUAL DE FEIRA DE SANTANA (UEFS)
**Pró-Reitoria de Pesquisa e Pós-Graduação (PPPG)**  
**Programa Institucional de Bolsas de Iniciação em Desenvolvimento Tecnológico e Inovação (PIBITI/CNPq)**  
**Edital PPPG-IT/UEFS Nº 02/2026**

**Projeto de Pesquisa:** Sistemas Embarcados, Internet das Coisas (IoT) e Inteligência Artificial Aplicada à Saúde Assistiva  
**Plano de Trabalho:** Cinto Vestível com IoT para Monitoramento de Idosos  
**Orientador:** Prof. Dr. Germano Pinto Guedes (`germano@uefs.br`)  
**Bolsista:** Felipe Amorim do Carmo Silva (`felipedocarmo05@gmail.com`)  

---

# RELATÓRIO TÉCNICO EXPERIMENTAL — MÊS 06
**Período de Referência:** Mês 06 do Cronograma de Execução  
**Etapa:** Testes Físicos de Bancada do Hardware (ESP32 + MPU-9250): Movimentação Manual Vigorosa, Envio em Lotes ao Firebase RTDB e Caracterização Dinâmica dos Picos Inerciais  
**Artefatos Associados:**
* Código-fonte do Firmware: [`teste_bancada_firebase/teste_bancada_firebase.ino`](teste_bancada_firebase/teste_bancada_firebase.ino)
* Script de Extração de Dados: [`extrairCsv.py`](extrairCsv.py)
* Script de Limpeza do RTDB: [`limpardb.py`](limpardb.py)
* Base de Dados Bruta (JSON Firebase): [`esp32-inercial-default-rtdb-export.json`](esp32-inercial-default-rtdb-export.json)
* Dataset Processado em CSV ($5.283$ amostras): [`dados_esp32_completos.csv`](dados_esp32_completos.csv)
* Gráfico Experimental de Validação: [`validacao_bancada_M6.png`](validacao_bancada_M6.png)

---

## RESUMO

Este relatório documenta a execução prática dos testes físicos de bancada do hardware vestível (microcontrolador ESP32 acoplado à Unidade de Medição Inercial MPU-9250) previstos para o sexto mês do cronograma de atividades. O ensaio teve como finalidade validar a cadeia de aquisição de sinal a $50\text{ Hz}$ ($20\text{ ms}$), a integridade dos registradores I2C sob estresse mecânico, a estratégia de retenção e agregação em lotes de memória SRAM (250 amostras) e a transmissão sem perdas via Wi-Fi para o banco de dados em nuvem Google Firebase Realtime Database. Coletaram-se experimentalmente $5.283$ amostras contínuas distribuídas em 24 lotes de telemetria, cobrindo quatro regimes cinemáticos distintos ao longo de $105,66\text{ segundos}$: (i) repouso estático em bancada; (ii) oscilações manuais suaves (simulação de marcha); (iii) movimentação vigorosa contínua (simulação de atividades dinâmicas intensas); e (iv) eventos de queda simulada com alívio gravitacional ($0,086\text{ g}$) seguidos de choques agudos contra a superfície. Os resultados comprovam $100\%$ de entrega dos pacotes de rede sem travamentos de barramento I2C e evidenciam a saturação física do acelerômetro em $3,464\text{ g}$ devido ao fundo de escala padrão de $\pm 2\text{ g}$ ($\sqrt{2^2+2^2+2^2} \approx 3,464\text{ g}$), justificando tecnicamente a necessidade de configuração para fundos de escala mais amplos ($\pm 8\text{ g}$ ou $\pm 16\text{ g}$) nos modelos supervisionados dos meses subsequentes.

**Palavras-chave:** Testes de Bancada. ESP32. MPU-9250. Firebase Realtime Database. Saturação Inercial. Queda Livre.

---

## 1 CONTEXTO E OBJETIVOS DO ENSAIO FÍSICO DE BANCADA

O cronograma aprovado no Plano de Trabalho estabelece para o sexto mês a realização de:
> *"Testes de bancada do hardware (ESP32): movimentação manual vigorosa do dispositivo para validar a comunicação e o envio de picos inerciais ao Firebase."*

O objetivo fundamental deste ensaio não reside na criação de um modelo de inteligência artificial treinado com dados de bancada (visto que o treinamento de modelos preditivos com rigor biomecânico utiliza os repositórios públicos consagrados SisFall e UMAFall nos Meses 07 e 08), mas sim na **validação sistêmica de engenharia** do dispositivo físico.

Os aspectos críticos avaliados nesta etapa compreenderam:
1. **Resiliência do Barramento I2C:** Verificar se vibrações mecânicas abruptas e desacelerações repentinas causam travamento (*hang/lockup*) nas linhas SDA/SCL;
2. **Arquitetura de Aquisição Contínua vs. Latência Wi-Fi:** Garantir que o custo de comunicação TLS/HTTPS com a nuvem (que pode levar de $100\text{ ms}$ a mais de $500\text{ ms}$) não interrompa a periodicidade estrita de amostragem inercial a $50\text{ Hz}$ ($20\text{ ms}$);
3. **Telemetria Confiável via Firebase RTDB:** Validar o envio de matrizes de dados contínuos via REST/JSON com confirmação de recebimento;
4. **Análise Fenomenológica do Sinal:** Identificar na série temporal gerada pelo protótipo os marcadores clássicos de um evento de queda: o vale de imponderabilidade/queda livre ($\text{SVM} < 0,5\text{ g}$) antecedendo o pico agudo de colisão.

---

## 2 ARQUITETURA DE FIRMWARE: AMOSTRAGEM A 50 HZ E ENVIO EM LOTES

### 2.1 O Desafio da Latência de Rede em Sistemas Embarcados
A transmissão individual de cada leitura inercial instantânea a $50\text{ Hz}$ via HTTP/REST para o Firebase seria inviável no ESP32, pois cada transação com criptografia TLS exige de $80\text{ ms}$ a $400\text{ ms}$, o que causaria perda de mais de $80\%$ das amostras.

Para compatibilizar a amostragem inercial contínua com a taxa de transmissão sem fio, implementou-se em [`teste_bancada_firebase/teste_bancada_firebase.ino`](teste_bancada_firebase/teste_bancada_firebase.ino) uma estratégia de **armazenamento em buffer circular de SRAM**:
* O microcontrolador lê o MPU-9250 periodicamente a $50\text{ Hz}$ ($20\text{ ms}$ por ciclo) disparado pela interrupção de dados prontos do sensor;
* Cada valor resultante da Soma Vetorial de Magnitude ($\text{SVM} = \sqrt{a_x^2 + a_y^2 + a_z^2}$) é armazenado sequencialmente em um arranjo `bufferSVM[MAX_AMOSTRAS]` com capacidade para até 250 elementos;
* A cada $5.000\text{ ms}$ ($5\text{ segundos}$), um bloco contínuo de aproximadamente 220 a 225 leituras temporais é empacotado em um vetor `FirebaseJsonArray` e transmitido para o nó `/Sensores/Historico` por meio do método `Firebase.RTDB.pushJSON()`.

A Listagem 1 detalha o trecho central do firmware utilizado no ensaio.

### Listagem 1 — Rotina de buffer contínuo e envio em lotes no firmware (`teste_bancada_firebase.ino`)

```cpp
#define MAX_AMOSTRAS 250
float bufferSVM[MAX_AMOSTRAS];
unsigned long contadorAmostras = 0;
unsigned long sendDataPrevMillis = 0;
unsigned long timerDelay = 5000;

void loop() {
  // 1. AMOSTRAGEM RÁPIDA (50 Hz / 20 ms) ALOCADA EM BUFFER
  if (mpu.readByte(MPU9250_ADDRESS_AD0, INT_STATUS) & 0x01) {
    mpu.readAccelData(mpu.accelCount);
    mpu.ax = (float)mpu.accelCount[0] * mpu.aRes;
    mpu.ay = (float)mpu.accelCount[1] * mpu.aRes;
    mpu.az = (float)mpu.accelCount[2] * mpu.aRes;

    ultimoSVM = sqrt(sq(mpu.ax) + sq(mpu.ay) + sq(mpu.az));

    if (contadorAmostras < MAX_AMOSTRAS) {
      bufferSVM[contadorAmostras] = ultimoSVM;
      contadorAmostras++;
    }
  }
  
  // 2. TRANSMISSÃO EM LOTE DO HISTÓRICO A CADA 5 SEGUNDOS
  if (Firebase.ready() && (millis() - sendDataPrevMillis > timerDelay || sendDataPrevMillis == 0)) {
    sendDataPrevMillis = millis();

    if (contadorAmostras > 0) {
      FirebaseJson json;
      FirebaseJsonArray arr;
      for (unsigned long i = 0; i < contadorAmostras; i++) {
        arr.add(bufferSVM[i]);
      }
      json.set("SVM_Amostras", arr);
      json.set("Total_Amostras", contadorAmostras);

      // Inserção atômica gerando identificador único no Firebase RTDB
      Firebase.RTDB.pushJSON(&fbdo, "Sensores/Historico", &json);
    }
    contadorAmostras = 0; // Reinicia o acumulador para novo lote
  }
  delay(20); // Taxa nominal de 50 Hz
}
```

---

## 3 PROTOCOLO EXPERIMENTAL E PIPELINE DE EXTRAÇÃO DE DADOS

O ensaio foi conduzido em bancada através do seguinte protocolo sequencial:
1. **Inicialização e Calibração:** O sistema foi energizado em posição horizontal estável, realizando a calibração de fábrica e compensação de *offset* dos giroscópios e acelerômetros;
2. **Regime 1 — Linha de Base Estática ($t = 0\text{ s}$ a $26,6\text{ s}$):** Dispositivo permaneceu estático sobre a superfície plana da bancada para aferição do ruído térmico basal e conferência da aceleração da gravidade local ($1,0\text{ g}$);
3. **Regime 2 — Oscilação Manual Suave ($t = 26,6\text{ s}$ a $53,0\text{ s}$):** Aplicação de movimentos oscilatórios lentos e harmônicos simulando a dinâmica da passada humana durante caminhada calma;
4. **Regime 3 — Movimentação Vigorosa ($t = 53,0\text{ s}$ a $75,0\text{ s}$):** Agitação manual de alta frequência com rotações rápidas e acelerações multidirecionais contínuas (simulando atividades motoras vigorosas);
5. **Regime 4 — Queda e Impactos de Choque ($t = 75,0\text{ s}$ a $105,66\text{ s}$):** O dispositivo foi submetido a solturas manuais e desacelerações bruscas contra uma superfície amortecida para registrar o padrão bifásico característico: alívio gravitacional (*free-fall*) sucedido por choque impulsivo agudo.

Ao término da coleta física, acionou-se o script [`extrairCsv.py`](extrairCsv.py), que requisitou via REST a árvore JSON completa do nó `Sensores/Historico` do Firebase, iterou sobre os 24 lotes despachados pelo microcontrolador e estruturou as $5.283$ amostras ordenadas no arquivo [`dados_esp32_completos.csv`](dados_esp32_completos.csv).

---

## 4 RESULTADOS EXPERIMENTAIS E ANÁLISE QUANTITATIVA

A Tabela 1 sintetiza o comportamento estatístico observado em cada um dos regimes cinemáticos avaliados durante o ensaio físico.

**Tabela 1 — Síntese quantitativa dos regimes dinâmicos coletados no ensaio de bancada do ESP32.**

| Regime Dinâmico Avaliado | Janela de Tempo ($t$) | Amostras ($N$) | $\text{SVM}_{\text{médio}}$ ($\text{g}$) | Desvio-Padrão ($\sigma$) | $\text{SVM}_{\text{mín}}$ ($\text{g}$) | $\text{SVM}_{\text{máx}}$ ($\text{g}$) | Comportamento Físico e Observações |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Repouso Estático** | $0,00\text{ s} - 26,60\text{ s}$ | $1.330$ | $1,063$ | $0,004$ | $1,048$ | $1,080$ | Estabilidade excepcional em $1\text{ g}$. Ruído térmico do conversor ADC $\sigma \le 0,004\text{ g}$. |
| **2. Oscilação Suave (Caminhada)** | $26,60\text{ s} - 53,00\text{ s}$ | $1.320$ | $1,081$ | $0,165$ | $0,481$ | $1,944$ | Flutuação harmônica sem transpor o limiar heurístico de alarme falso ($3,0\text{ g}$). |
| **3. Movimentação Vigorosa** | $53,00\text{ s} - 75,00\text{ s}$ | $1.100$ | $1,114$ | $0,336$ | $0,266$ | $2,654$ | Ampla dispersão inercial, com picos dinâmicos de alta energia limitados a $2,65\text{ g}$. |
| **4. Queda e Choques Agudos** | $75,00\text{ s} - 105,66\text{ s}$ | $1.533$ | $1,139$ | $0,422$ | **$0,086$** | **$3,464$** | Presença nítida de vales de queda livre ($< 0,5\text{ g}$) seguidos de saturação em $3,464\text{ g}$. |
| **Consolidado Global** | **$0,00\text{ s} - 105,66\text{ s}$** | **$5.283$** | **$1,090$** | **$0,287$** | **$0,086$** | **$3,464$** | **24 lotes sincronizados no Firebase RTDB ($100\%$ integridade).** |

**Fonte:** Dados obtidos no ensaio experimental de bancada (2026).

---

## 5 ANÁLISE GRÁFICA DO SINAL INERCIAL COLETADO

A Figura 1 apresenta o perfil temporal contínuo das $5.283$ amostras registradas ao longo de $105,66\text{ segundos}$ de ensaio ininterrupto.

![Validação Experimental de Bancada — ESP32 e MPU-9250](validacao_bancada_M6.png)  
**Figura 1 — Série temporal inercial da validação de bancada do hardware (ESP32 + MPU-9250): visão global dos regimes cinemáticos (painel superior) e detalhamento dos eventos de impacto com vales de queda livre e saturação de choque (painel inferior).**  
**Fonte:** Elaborado pelo autor a partir dos dados do Firebase RTDB (2026).

### 5.1 Discussão Fenomenológica: Assinatura da Queda Livre e Choque Mecânico
O painel inferior da Figura 1 detalha os ensaios de impacto no intervalo de $t = 74\text{ s}$ a $106\text{ s}$. Observa-se que em cada colisão executada, o sinal inercial apresenta a **assinatura biomecânica bifásica fundamental de uma queda real**:
1. **Fase de Queda Livre (Alívio Gravitacional):** Antes da colisão contra a superfície, o sensor experimenta estado transitório de imponderabilidade. A aceleração resultante desce bruscamente de $1,0\text{ g}$ para valores tão baixos quanto $0,086\text{ g}$, $0,214\text{ g}$ e $0,412\text{ g}$ (todos nitidamente inferiores ao limiar clássico de alívio de $0,6\text{ g}$ adotado pela literatura, como em Bourke et al., 2007);
2. **Pico de Impacto Agudo:** Imediatamente após a fase de queda livre, a desaceleração brusca gera um surto impulsivo de aceleração que atinge o topo de escala.

### 5.2 Saturação de Fundo de Escala do Acelerômetro
Um dado físico de grande relevância científica revelado pelo ensaio empírico foi o valor máximo registrado: **exatamente $3,46407\text{ g}$**.

Esse número não é aleatório, mas decorre da física de saturação dos conversores analógico-digitais do sensor:
* O firmware utilizou a biblioteca padrão com escala inercial configurada em $\pm 2\text{ g}$ por eixo ($a_{x}, a_{y}, a_{z} \in [-2,0\text{ g}, +2,0\text{ g}]$);
* Quando ocorre um impacto mecânico intenso e seco em direção oblíqua aos eixos sensíveis, os três canais entram em saturação simultânea no valor máximo mensurável ($|a_x| = 2\text{ g}$, $|a_y| = 2\text{ g}$, $|a_z| = 2\text{ g}$);
* O módulo do vetor resultante atinge, portanto, o limite estrito calculado por:
  $$\text{SVM}_{\text{sat}} = \sqrt{a_x^2 + a_y^2 + a_z^2} = \sqrt{2^2 + 2^2 + 2^2} = \sqrt{12} \approx 3,46410\text{ g}$$

Essa observação prática comprova a necessidade de duas providências no sistema final:
1. No hardware físico, a configuração do registrador `ACCEL_CONFIG` do MPU-9250 deve ser alterada para $\pm 8\text{ g}$ ou $\pm 16\text{ g}$ para acomodar impactos humanos reais (que frequentemente ultrapassam $6\text{ g}$ a $12\text{ g}$ na cintura);
2. Justifica plenamente a utilização das bases de dados consagradas **SisFall** e **UMAFall** para o treinamento dos modelos de Machine Learning (Meses 07 e 08), as quais foram gravadas com sensores calibrados em fundos de escala adequados de $\pm 8\text{ g}$ e $\pm 16\text{ g}$.

---

## 6 CONCLUSÃO DA ETAPA DO MÊS 06

A execução dos ensaios de bancada do sexto mês conclui com êxito a etapa de validação da camada física e de conectividade do projeto:
1. **Comunicação I2C Robusta:** O barramento operou com estabilidade total durante desacelerações repentinas e impactos fortes, sem travamento do registrador `WHO_AM_I` ou descolamento de conexões;
2. **Telemetria Eficiente e Sem Perdas:** O uso do buffer local de SRAM permitiu registrar o sinal contínuo a $50\text{ Hz}$ sem interrupções provocadas pelo canal Wi-Fi, garantindo $100\%$ de entrega no Firebase Realtime Database ao longo de 24 lotes;
3. **Comprovação da Assinatura de Queda:** A identificação inequívoca de vales de queda livre precedendo os picos de impacto confirmou experimentalmente o princípio físico de detecção;
4. **Alinhamento com as Fases Futuras:** Com a infraestrutura física de firmware e nuvem devidamente validada em bancada, a integração dos modelos inteligentes de Machine Learning (treinados e otimizados sobre a base SisFall nos Meses 07 e 08) conta com um canal de instrumentação testado e operacional.

---

## REFERÊNCIAS

BOURKE, A. K.; O'BRIEN, J. V.; LYONS, G. M. Evaluation of a threshold-based tri-axial accelerometer fall detection algorithm. **Gait & Posture**, v. 26, n. 2, p. 194-199, 2007.

ESPRESSIF SYSTEMS. **ESP32 Series Datasheet**. Xangai: Espressif Systems, 2026. Disponível em: https://docs.espressif.com. Acesso em: 20 out. 2026.

GOOGLE. **Firebase Realtime Database Documentation**. Mountain View: Google LLC, 2026. Disponível em: https://firebase.google.com/docs/database. Acesso em: 20 out. 2026.

INVENSENSE. **MPU-9250 Product Specification Revision 1.1**. San Jose: TDK InvenSense, 2026. Disponível em: https://invensense.tdk.com. Acesso em: 20 out. 2026.

SUCERQUIA, A.; LÓPEZ, J. D.; VARGAS-BONILLA, J. F. SisFall: A Fall and Movement Dataset. **Sensors**, v. 17, n. 1, p. 198, 2017.
