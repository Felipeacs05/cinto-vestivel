import requests
import pandas as pd

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
    df.to_csv("dados_esp32_completos.csv", index=False)
    print(f"Sucesso! {len(df)} amostras individuais salvas em 'dados_esp32_completos.csv'.")
else:
    print("Nenhum dado encontrado em Sensores/Historico.")