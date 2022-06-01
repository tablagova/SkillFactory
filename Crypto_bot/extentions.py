import requests
import json
from config import currencies


class ConversionException(Exception):
    pass


class CryptoConverter:
    @staticmethod
    def get_price(base: str, quote: str, amount: str):
        try:
            base_id = currencies[base]['id']
        except KeyError:
            raise ConversionException(f'Не удалось обработать валюту \"{base}\"')

        try:
            quote_symbol = currencies[quote]['symbol']
        except KeyError:
            raise ConversionException(f'Не удалось обработать валюту \"{quote}\"')

        try:
            amount = float(amount)
        except ValueError:
            raise ConversionException(f'Не удалось обработать количество \"{amount}\"')

        if base == quote:
            raise ConversionException(f'Невозможно перевести в ту же валюту: из {base} в {quote}')

        rate = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={base_id}&vs_currencies={quote_symbol}')

        return json.loads(rate.content)[base_id][quote_symbol] * amount
