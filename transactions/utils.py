import requests

def get_currency_exchange_rate(base_currency, target_currency):
    print("from---- before utils")
    # api_key = "71ffc1ff995e4b4fb15ab00965267f2d"
    url = "https://api.fastforex.io/fetch-all?api_key=ec683d1e20-46e31aa18c-rzztbe"
    print("from after utils ---------")
    
    response = requests.get(url)
    data = response.json()
    
    base_rate = data['results'][base_currency]
    target_rate = data['results'][target_currency]
    
    exchange_rate = target_rate / base_rate
    return exchange_rate

def convert_currency(amount, exchange_rate):
    return amount * exchange_rate

def get_country_info(currency_code):
    url = f"https://restcountries.com/v3.1/currency/{currency_code}"
    
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200 and len(data) > 0:
        country_data = data[0]
        name = country_data['name']['common']
        flag = country_data['flags'][0]
        return name, flag
    else:
        return None, None

