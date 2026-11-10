import requests

url = "https://esp32-inercial-default-rtdb.firebaseio.com/Sensores.json"
resposta = requests.delete(url)

if resposta.status_code == 200:
    print("Dados apagados com sucesso!")
else:
    print(f"Erro ao apagar: {resposta.status_code} - {resposta.text}")