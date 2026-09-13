import requests
from dotenv import load_dotenv
import os

from currency_codes import get_currency_code

load_dotenv("../.env")
api_key = os.getenv("EXCHANGERATE_API_KEY") 


def currency_conversion(amount: float, base_currency: str, target_currency: str) -> float:
    try:
        base_currency = get_currency_code(base_currency)
        target_currency = get_currency_code(target_currency)

        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base_currency}/{target_currency}"

        response =  requests.get(url=url)

        if response.status_code==200:
            data = response.json()
            conversion_rate = data['conversion_rate']
            converted_amount = float(amount*conversion_rate)
        else:
            raise ValueError(f"Could not fetch Currency conversion API: {response.status_code}")

        return converted_amount
        
    except Exception as e:
        raise ValueError(f"Currency conversion failed: {e}")