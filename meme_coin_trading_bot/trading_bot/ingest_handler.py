import requests
import time 
import re
import datetime
import pytz
from .models import Categories, MemeCoins, MemeCoinCategories, MarketData


class IngestAPIHandler:
    def __init__(self):
        """
            This class uses CryptoCompare API to fetch data
        """
        self.base_url = "https://min-api.cryptocompare.com/"

    def fetch_all_coins(self):
        url = f"{self.base_url}data/all/coinlist"

        response = requests.get(url)
        if response.status_code == 200:
            return response.json()["Data"]
        else:
            return None
    

    def is_meme_coin(self, coin_data):
        """Advanced meme coin detection using 7+ factors"""
        name = coin_data['Name'].lower()
        symbol = coin_data['Symbol'].lower()
        description = coin_data.get('Description', '').lower()
        image = coin_data.get('ImageUrl', '').lower()

        # Pattern database (expandable list)
        meme_patterns = {
            'name_keywords': ['meme', 'doge', 'shib', 'floki', 'pepe', 'elon', 'sats', 'bonk'],
            'symbol_format': r'\$?[A-Z]{3,5}\d*$',  # Matches formats like DOGE, PEPE2, $SHIB
            'animal_words': ['inu', 'kitty', 'woof', 'meow', 'hamster'],
            'meme_references': ['wojak', 'diamond hands', 'to the moon', 'ngmi'],
            'supply_indicators': ['quadrillion', 'trillion', 'billion supply'],
            'mascot_check': bool(coin_data.get('LogoUrl'))
        }

        # Scoring system
        score = 0

        # Name analysis
        score += 2 if any(kw in name for kw in meme_patterns['name_keywords']) else 0
        score += 1 if re.search(r'(.+)(inu|coin|dog|cat)$', name) else 0

        # Symbol analysis
        score += 2 if re.match(meme_patterns['symbol_format'], coin_data['Symbol']) else 0

        # Description analysis
        score += 1.5 if any(kw in description for kw in meme_patterns['meme_references']) else 0
        score += 1 if any(aw in description for aw in meme_patterns['animal_words']) else 0
        score += 1 if any(si in description for si in meme_patterns['supply_indicators']) else 0

        # Social proof indicators
        score += 1.5 if coin_data.get('SocialMentions', 0) > 1000 else 0
        score += 1 if coin_data.get('RedditSubscribers', 0) > 5000 else 0

        return score >= 3  # Threshold for meme classification


    def fetch_coin_data(self, coin_id, currency="USD"):
        url = f"{self.base_url}data/pricemultifull?fsyms={coin_id}&tsyms={currency}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None



class IngestDBHandler:
    def __init__(self):
        pass

    def save_categories(self, categories):
        for category in categories:
            Categories.objects.get_or_create(
                category_id=category.get("category_id"), 
                category_name=category.get("name")
                )
    
    def save_meme_coins(self, coins):
        for coin in coins:
            try:
                obj, created = MemeCoins.objects.get_or_create(
                    coin_id=coin.get("Name"),
                    defaults={
                        "coin_name": coin.get("CoinName"), 
                        "coin_full_name": coin.get("FullName"), 
                        "coin_symbol": coin.get("Symbol"), 
                        "coin_description": coin.get("Description"), 
                        "total_coins_mined": coin.get("TotalCoinsMined"),
                        "coin_creation_date": coin.get("AssetLaunchDate")
                        }
                )
                if created:
                    print("Coin inserted")
                else:
                    print("Coin already exists")
            except Exception as e:
                print(f"Duplicate entry detected for {coin.get('Name')}. Skipping...")
    

    def save_meme_coin_categories(self, coins):
        for coin in coins:
            categories = coin.get("categories")
            for category in categories:
                MemeCoinCategories.objects.get_or_create(
                    coin_id=MemeCoins.objects.get(coin_id=coin.get("id")),
                    category_id=Categories.objects.get(category_id=category)
                )


    def save_market_data(self, coin_name, coin_symbol, currency, coin_data):
        try:
            coin_data = coin_data["RAW"][coin_symbol][currency]
            if coin_data.get("LASTUPDATE"):
                date = datetime.datetime.fromtimestamp(coin_data.get("LASTUPDATE"))
            else:
                date = None
            print(" Coin: ", coin_name)
        
            obj, created = MarketData.objects.get_or_create(
                coin_id=coin_name,
                market=coin_data.get("MARKET"),
                last_updated=date,
                price=coin_data.get("PRICE"),
                currency=coin_data.get("TOSYMBOL"),
                high_24h=coin_data.get("HIGH24HOUR"),
                low_24h=coin_data.get("LOW24HOUR"),
                open_24h=coin_data.get("OPEN24HOUR"),
                last_volume_base=coin_data.get("LASTVOLUME"),
                last_volume_quote=coin_data.get("LASTVOLUMETO"),
                volume_24h_base=coin_data.get("VOLUME24HOUR"),
                volume_24h_quote=coin_data.get("VOLUME24HOURTO"),
                price_change_percentage_1h=coin_data.get("CHANGEPCTHOUR"),
                price_change_percentage_24h=coin_data.get("CHANGEPCT24HOUR"),
                circulating_supply=coin_data.get("CIRCULATINGSUPPLY"),
                total_supply=coin_data.get("SUPPLY"),
                market_cap=coin_data.get("MKTCAP"),
                market_cap_rank=coin_data.get("MKTCAPRANK"),
                bid_ask_spread=coin_data.get("BIDASKSPREAD"),
                liquidity_score=coin_data.get("LIQUIDITYSCORE"),
                conversion_type=coin_data.get("CONVERSIONTYPE"),
                conversion_symbol=coin_data.get("CONVERSIONSYMBOL")
            )
            if created:
                print("Coin inserted")
            else:
                print("Coin already exists")
        except Exception as e:
            print(f"Error: ", e)