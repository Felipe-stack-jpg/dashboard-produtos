import requests
import pandas as pd

def carregar_dados():
    url = 'https://fakestoreapi.com/products'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        return df
    else:
        return None