# crypto/trading_algorithm.py
from utils import fetch_meme_coins

def trading_decision(coin):
    # Define thresholds for decision making
    buy_threshold_price_change = 2.0  # Buy if price change percentage is above this
    sell_threshold_price_change = -2.0  # Sell if price change percentage is below this
    volume_threshold = 1000000  # Minimum volume to consider a trade
    ath_threshold = -50.0  # Consider buying if the price is 50% below ATH

    # Extract relevant data
    current_price = coin['current_price']
    price_change_24h = coin['price_change_percentage_24h']
    total_volume = coin['total_volume']
    ath_change_percentage = coin['ath_change_percentage']

    # Decision logic
    if price_change_24h > buy_threshold_price_change and total_volume > volume_threshold:
        if ath_change_percentage < ath_threshold:            
            return f"Buy {coin['name']} at ${current_price:.2f}"
    elif price_change_24h < sell_threshold_price_change:
        return f"Sell {coin['name']} at ${current_price:.2f}"
    else:
        return f"Hold {coin['name']}"

def main():
    # Fetch meme coins data
    meme_coins = fetch_meme_coins()
    if meme_coins:
        for coin in meme_coins:
            decision = trading_decision(coin)
            print(decision)
    else:
        print("Failed to fetch meme coins data.")

if __name__ == "__main__":
    main()