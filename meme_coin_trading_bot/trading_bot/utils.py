# crypto/utils.py
import requests

def fetch_meme_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets"   # base api url 
        # https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=meme-token 
    params = {
        'vs_currency': 'usd',
        'category': 'meme-token',
        'order': 'market_cap_desc',
        'per_page': 100,
        'page': 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return parse_meme_coins(response.json())
    else:
        return None

def parse_meme_coins(data):
    parsed_data = []
    for coin in data:
        parsed_data.append({
            'id': coin.get('id'),
            'symbol': coin.get('symbol'),
            'name': coin.get('name'),
            'image': coin.get('image'),
            'current_price': coin.get('current_price'),
            'market_cap': coin.get('market_cap'),
            'market_cap_rank': coin.get('market_cap_rank'),
            'fully_diluted_valuation': coin.get('fully_diluted_valuation'),
            'total_volume': coin.get('total_volume'),
            'high_24h': coin.get('high_24h'),
            'low_24h': coin.get('low_24h'),
            'price_change_24h': coin.get('price_change_24h'),
            'price_change_percentage_24h': coin.get('price_change_percentage_24h'),
            'market_cap_change_24h': coin.get('market_cap_change_24h'),
            'market_cap_change_percentage_24h': coin.get('market_cap_change_percentage_24h'),
            'circulating_supply': coin.get('circulating_supply'),
            'total_supply': coin.get('total_supply'),
            'max_supply': coin.get('max_supply'),
            'ath': coin.get('ath'),
            'ath_change_percentage': coin.get('ath_change_percentage'),
            'ath_date': coin.get('ath_date'),
            'atl': coin.get('atl'),
            'atl_change_percentage': coin.get('atl_change_percentage'),
            'atl_date': coin.get('atl_date'),
            'roi': coin.get('roi'),
            'last_updated': coin.get('last_updated'),
        })
    return parsed_data