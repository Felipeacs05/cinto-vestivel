import os
import requests
import pandas as pd
from analise_bancada_mes6 import analisar_e_gerar_grafico

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
CAMINHO_CSV = os.path.join(DIRETORIO_ATUAL, "dados_esp32_completos.csv")

url = "https://esp32-inercial-default-rtdb.firebaseio.com/Sensores/Historico.json"
dados = requests.get(url).json()

todas_amostras = []

if dados:
    for id_lote, conteudo in dados.items():
        lista_svm = conteudo.get("SVM_Amostras", [])
        for valor in lista_svm:
            todas_amostras.append({
                "ID_Lote": id_lote,
                "SVM": valor
            })
            
    df = pd.DataFrame(todas_amostras)
    df.to_csv(CAMINHO_CSV, index=False)
    print(f"Sucesso! {len(df)} amostras individuais salvas em '{CAMINHO_CSV}'.\n")
    
    # Gera automaticamente o relatório estatístico e o gráfico validacao_bancada_M6.png
    analisar_e_gerar_grafico()
else:
    print("Nenhum dado encontrado em Sensores/Historico.")
