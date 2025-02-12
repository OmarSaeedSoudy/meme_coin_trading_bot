import requests
import time 
from .models import Categories, MemeCoins, MemeCoinCategories, MarketData


class IngestAPIHandler:
    def __init__(self):
        """
            This class uses CoinGecko API to fetch data
        """
        self.base_url = "https://api.coingecko.com/api/v3/"
    

    def fetch_all_categories(self):
        url = f"{self.base_url}coins/categories/list"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
        
    def fetch_meme_categories(self):
        categories = self.fetch_all_categories()
        meme_categories = []
        for category in categories:
            if "meme" in category.get("name").lower():
                meme_categories.append(category)
        return meme_categories


    def fetch_meme_coins(self):
        index = 1
        """
        Fetches meme coins market data.
        """
        coins = []
        url = f"{self.base_url}coins/markets"
        params = {
            "vs_currency": "usd",
            "category": "meme-token",
            "page": 1,
            "per_page": 250,
            "sparkline": True
        }
        response = requests.get(url, params=params)
        
        while response.status_code == 200:
            index += 1
            coins.extend(response.json())
            if len(response.json()) < 100:
                break
            params["page"] += 1
            time.sleep(10)
            response = requests.get(url, params=params)
        
        print("INDEXXXXX: ", index)
        return coins

    def fetch_coin_data(self, coin_id):
        url = f"{self.base_url}coins/{coin_id}"
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
                    coin_id=coin.get("id"),
                    defaults={"name": coin.get("name"), "image_url": coin.get("image")}
                )
                if created:
                    print("Coin inserted")
                else:
                    print("Coin already exists")
            except Exception as e:
                print(coin)
                print(f"Duplicate entry detected for {coin.get('id')}. Skipping...")


            # categories = coin.get("categories")
            # for category in categories:
            #     tuned_category = category.lower().replace(" ", "-")
            #     category_exists = Categories.objects.filter(category_id=tuned_category).exists()
            #     print("category_exists: ", category_exists)
            #     if not category_exists:
            #         tuned_category = 'unknown'
            #     print("Coin:", coin.get("id"), "Category:", tuned_category)
            #     MemeCoinCategories.objects.get_or_create(
            #         coin_id=MemeCoins.objects.get(coin_id=coin.get("id")),
            #         category_id=Categories.objects.get(category_id=tuned_category)
            #     )
            # print("**************************************************************************")
    

    def save_meme_coin_categories(self, coins):
        for coin in coins:
            categories = coin.get("categories")
            for category in categories:
                MemeCoinCategories.objects.get_or_create(
                    coin_id=MemeCoins.objects.get(coin_id=coin.get("id")),
                    category_id=Categories.objects.get(category_id=category)
                )

    def save_market_data(self, coins):
        for coin in coins:
            MarketData.objects.get_or_create(
                coin=MemeCoins.objects.get(coin_id=coin.get("id")),
                timestamp=coin.get("market_data").get("last_updated"),
                market_cap=coin.get("market_data").get("market_cap"),
                total_volume=coin.get("market_data").get("total_volume"),
                price=coin.get("market_data").get("current_price"),
                price_change_1h=coin.get("market_data").get("price_change_percentage_1h_in_currency"),
                price_change_24h=coin.get("market_data").get("price_change_percentage_24h_in_currency"),
                liquidity_score=coin.get("market_data").get("liquidity_score")
            )



def main():

    print("Ingesting data...")
    ingest_handler = IngestAPIHandler()
    db_handler = IngestDBHandler()
    # categories = ingest_handler.fetch_all_categories()
    coins = ingest_handler.fetch_meme_coins()
    # main_coins = []
    # for coin in coins:
    #     coin_data = ingest_handler.fetch_coin_data(coin.get("id"))
    #     if coin_data:
    #         main_coins.append(coin_data)

    # db_handler.save_categories(categories)
    db_handler.save_meme_coins(coins)
    # db_handler.save_market_data(coins)
    print("Data ingested successfully.")
