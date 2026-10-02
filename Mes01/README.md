# UNIVERSIDADE ESTADUAL DE FEIRA DE SANTANA (UEFS)
**Pró-Reitoria de Pesquisa e Pós-Graduação (PPPG)**  
**Programa Institucional de Bolsas de Iniciação em Desenvolvimento Tecnológico e Inovação (PIBITI/CNPq)**  
**Edital PPPG-IT/UEFS Nº 02/2026**

**Projeto de Pesquisa:** Sistemas Embarcados, Internet das Coisas (IoT) e Inteligência Artificial Aplicada à Saúde Assistiva  
**Plano de Trabalho:** Cinto Vestível com IoT para Monitoramento de Idosos  
**Orientador:** Prof. Dr. Germano Pinto Guedes (`germano@uefs.br`)  
**Bolsista:** Felipe Amorim do Carmo Silva (`felipedocarmo05@gmail.com`)  

---

# RELATÓRIO TÉCNICO PARCIAL — MÊS 01
**Período de Referência:** Mês 01 do Cronograma de Execução  
**Etapa:** Revisão Bibliográfica Sistemática e Especificação dos Componentes de Hardware  

---

## RESUMO

Este documento apresenta os resultados referentes ao primeiro mês de execução do plano de trabalho vinculado ao projeto de Iniciação Tecnológica. As atividades concentraram-se em duas frentes complementares: (i) a condução de uma revisão bibliográfica sobre sistemas de detecção de quedas em idosos, limitações de algoritmos baseados em limiares heurísticos fixos, bases de dados inerciais públicas e aprendizado de máquina embarcado (*TinyML*); e (ii) o levantamento de requisitos elétricos, mecânicos e computacionais para o dimensionamento do dispositivo vestível de borda (*Edge Device*). Como resultado, consolidou-se a escolha da arquitetura composta pelo microcontrolador ESP32, unidade de medição inercial (IMU) MPU-9250 comunicando-se via barramento I2C, bateria de polímero de lítio (LiPo) de 3,7 V e indicador luminoso local em LED.

**Palavras-chave:** Detecção de Quedas. Sistemas Embarcados. Sensoriamento Inercial. SisFall. TinyML.

---

## 1 INTRODUÇÃO E CONTEXTUALIZAÇÃO

O envelhecimento demográfico impõe demandas crescentes aos sistemas de assistência à saúde, destacando-se os acidentes por queda como uma das principais causas de hospitalização, perda de autonomia funcional e mortalidade entre indivíduos idosos (IGUAL; MEDRANO; PLAZA, 2013). A literatura médica e de engenharia biomédica aponta que o intervalo de tempo decorrido entre o colapso postural e o atendimento de socorro — frequentemente denominado *long-lie* — relaciona-se diretamente com o prognóstico clínico do paciente. Nesse contexto, dispositivos vestíveis (*wearables*) dedicados ao monitoramento cinemático contínuo atuam como ferramentas assistivas capazes de identificar o evento crítico de forma autônoma e acionar redes de suporte familiar ou hospitalar.

Os primeiros sistemas vestíveis descritos na literatura basearam-se predominantemente em algoritmos heurísticos de limiar fixo (*threshold-based algorithms*), nos quais o alarme é disparado sempre que a magnitude da aceleração resultante ultrapassa um valor predefinido, tipicamente situado entre $2,5\text{ g}$ e $3,5\text{ g}$ (BOURKE; O'BRIEN; LYONS, 2007). Embora apresentem reduzido custo computacional, tais métodos sofrem de uma limitação estrutural: Atividades de Vida Diária (ADLs, do inglês *Activities of Daily Living*) que envolvem movimentos rápidos ou impactos naturais — como sentar-se bruscamente em uma poltrona, subir escadas de forma acelerada ou trotar — frequentemente produzem picos transientes superiores ao limiar configurado, resultando em elevadas taxas de falsos positivos. Em contrapartida, quedas lentas decorrentes de síncopes ou escorregamentos amparados por mobília podem apresentar picos inferiores ao limiar, ocasionando falsos negativos críticos (SUCERQUIA; LÓPEZ; VARGAS-BONILLA, 2017).

A consolidação de técnicas de Inteligência Artificial embarcada (*Edge AI* / *TinyML*) permite contornar essa fragilidade ao substituir regras rígidas por classificadores supervisionados treinados para reconhecer a morfologia completa do sinal no domínio do tempo (WARDEN; SITUNAYAKE, 2019). Para tanto, faz-se necessária a fundamentação rigorosa das bases de dados de treinamento e da plataforma física de aquisição inercial, objeto deste primeiro mês de atividades.

---

## 2 REVISÃO BIBLIOGRÁFICA E ANÁLISE DE DATASETS PÚBLICOS

A construção de modelos de aprendizado de máquina voltados à cinemática humana exige conjuntos de dados representativos, amostrados em taxas compatíveis com a dinâmica do impacto e isentos de vieses populacionais. Durante o primeiro mês, foram analisadas as duas principais bases públicas de referência estipuladas no Plano de Trabalho: **SisFall** e **UMAFall**.

### 2.1 O Dataset SisFall e o Viés Etário na Cinemática

Desenvolvido por Sucerquia, López e Vargas-Bonilla (2017) na *Universidad de Antioquia*, o dataset **SisFall** constitui o referencial metodológico central deste projeto. Os autores demonstraram empiricamente que modelos calibrados exclusivamente com voluntários jovens perdem sensibilidade ao serem testados em indivíduos idosos, uma vez que a dinâmica muscular, a rigidez articular e a velocidade de marcha alteram-se substancialmente com o envelhecimento.

A base é composta por **4.505 arquivos** de séries temporais coletados a uma frequência de amostragem de $f_s = 200\text{ Hz}$ por meio de um dispositivo fixado na cintura dos voluntários, abrangendo **38 participantes** divididos em dois grupos:
* **Grupo Adulto Jovem (`SA01` a `SA23`):** 23 voluntários com idades entre 19 e 30 anos, que executaram tanto 19 categorias de Atividades de Vida Diária (`D01` a `D19`) quanto 15 modalidades de quedas simuladas (`F01` a `F15`) sobre colchões de amortecimento;
* **Grupo Idoso (`SE01` a `SE15`):** 15 voluntários com idades entre 60 e 75 anos, submetidos às atividades cotidianas (`D`) para registrar a assinatura biomecânica real do corpo envelhecido sem exposição a riscos físicos (com exceção do voluntário `SE06`, especialista em judô, que também realizou ensaios de queda).

### 2.2 O Dataset UMAFall e a Escolha Topológica da Cintura

Complementarmente, analisou-se o estudo de Casilari, Santoyo-Ramón e Cano-García (2017), responsável pelo dataset **UMAFall** (531 arquivos). Os autores investigaram a influência do ponto de fixação anatômica do sensor inercial comparando cinco regiões do corpo: punho, tornozelo, bolso da calça, tórax e cintura. Os resultados comprovaram que extremidades apendiculares (como punho e tornozelo) sofrem acelerações espúrias severas decorrentes de gesticulações independentes do equilíbrio postural. A **cintura**, por situar-se próxima ao centro de massa (centro de gravidade) do corpo humano, apresentou a melhor relação sinal-ruído e a maior capacidade discriminativa entre quedas e ADLs, justificando tecnicamente o formato de **cinto vestível** adotado neste projeto.

**Quadro 1 — Síntese comparativa das bases de dados científicas analisadas no Mês 01.**

| Característica Técnica | Dataset SisFall | Dataset UMAFall |
| :--- | :--- | :--- |
| **Referência Principal** | Sucerquia, López e Vargas-Bonilla (2017) | Casilari, Santoyo-Ramón e Cano-García (2017) |
| **Volume de Dados** | 4.505 arquivos de ensaios inerciais | 531 arquivos de ensaios multissensoriais |
| **Participantes** | 38 voluntários (23 jovens `SA` e 15 idosos `SE`) | 17 voluntários |
| **Posição Anatômica** | Cintura (fixação rígida próxima ao centro de massa) | Cintura, tórax, punho, tornozelo e bolso |
| **Taxa de Amostragem ($f_s$)** | $200\text{ Hz}$ | $20\text{ Hz}$ a $200\text{ Hz}$ |
| **Variáveis Registradas** | Aceleração triaxial ($\pm 16\text{ g}$ / $\pm 8\text{ g}$) e Giroscópio | Aceleração triaxial, Giroscópio e Magnetômetro |

**Fonte:** Elaborado pelo autor com base em Sucerquia, López e Vargas-Bonilla (2017) e Casilari, Santoyo-Ramón e Cano-García (2017).

---

## 3 ESPECIFICAÇÃO DOS COMPONENTES DE HARDWARE

Com base nos requisitos de processamento em borda, conectividade sem fio e portabilidade anatômica, definiu-se a arquitetura física do protótipo de cinto inteligente. A Figura 1 esquematiza o fluxo de integração entre os módulos selecionados para o primeiro ciclo de 12 meses.

```
+-------------------------------------------------------------------+
|                   PROTÓTIPO DO CINTO VESTÍVEL                     |
|                                                                   |
|  +------------------+       Barramento I2C      +--------------+  |
