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

