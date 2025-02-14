import datetime
import pytz
import time
from django.db.models import OuterRef, Subquery
from django.db import transaction
from django.utils import timezone
from .ingest_handler import IngestAPIHandler, IngestDBHandler
from .filtering_handler import FilteringAlgorithm
from .execution_handler import ExecutionHandler, ExecutionError
from .models import Categories, MemeCoins, MemeCoinCategories, MarketData, Trades

class TradingBot:
    def __init__(self):
        self.trading_cycle = 15 # Minutes
        self.ingest_api_handler = IngestAPIHandler()
        self.ingest_db_handler = IngestDBHandler()
        self.filtering_algorithm = FilteringAlgorithm()
        self.execution_handler = ExecutionHandler()

        self.usd_amount_per_trade = 100


    def ingest_all_data(self):
        # Variables
        all_coins = self.ingest_api_handler.fetch_all_coins()
        meme_coins = []
        new_meme_coins = []
        last_coin = MemeCoins.objects.order_by('-coin_creation_date').first()
        utc = pytz.UTC

        # Filter out coins that are not trading
        for key, value in all_coins.items():
            if value.get("IsTrading", False):
                if self.ingest_api_handler.is_meme_coin(value):
                    meme_coins.append(value)

        # Insert only new meme coins
        for coin in meme_coins:
            asset_launch_date_str = coin.get("AssetLaunchDate")
            if not asset_launch_date_str or asset_launch_date_str == "0000-00-00":
                print(f"Skipping invalid date for coin: {coin.get('Name')}")
                continue  # Skip this coin

            asset_launch_date = utc.localize(datetime.datetime.strptime(asset_launch_date_str, '%Y-%m-%d'))
            last_coin_date = last_coin.coin_creation_date.astimezone(utc)
        
            if asset_launch_date > last_coin_date:
                new_meme_coins.append(coin)

        print("Number of new meme coins: ", len(new_meme_coins))
        self.ingest_db_handler.save_meme_coins(new_meme_coins)

        # Add SOL Coin
        meme_coins.append({"Name": "SOL", "Symbol": "SOL", "AssetLaunchDate": "2017-06-26"})


        # Save market data
        for coin in meme_coins:
            coin_data = self.ingest_api_handler.fetch_coin_data(coin.get("Symbol"))
            if coin_data:
                self.ingest_db_handler.save_market_data(coin.get("Name"), coin.get("Symbol"), "USD", coin_data)

        return True


    def get_newest_coins(self, desired_coint = 20):
        """
        Get newest coins from the database 
        """
        newest_coins = MemeCoins.objects.order_by('-coin_creation_date')[:desired_coint]
        return newest_coins

    def get_coin_data(self, coin_symbol):
        """S
        Get coin market data from the database
        """
        coin_data = MarketData.objects.filter(coin_id=coin_symbol).all()
        return coin_data

    def get_coin_insights(self, coin_symbol):
        """Get comprehensive insights for decision-making"""
        # Get latest entry for each market
        latest_subquery = MarketData.objects.filter(
            coin_id=coin_symbol,
            market=OuterRef('market')
        ).order_by('-last_updated').values('last_updated')[:1]

        latest_data = MarketData.objects.filter(
            coin_id=coin_symbol,
            last_updated=Subquery(latest_subquery)
        )

        if not latest_data.exists():
            return {}

        # Select market with highest volume
        market_data = latest_data.order_by('-volume_24h_base').first()

        # Calculate technical indicators
        rsi = self.calculate_rsi(coin_symbol, market_data.market)
        ma_50 = self.calculate_ma(coin_symbol, market_data.market, 50)
        ma_200 = self.calculate_ma(coin_symbol, market_data.market, 200)

        return {
            'symbol': coin_symbol,
            'market': market_data.market,
            'price': float(market_data.price),
            'currency': market_data.currency,
            'price_change_1h': float(market_data.price_change_percentage_1h),
            'price_change_24h': float(market_data.price_change_percentage_24h),
            'volume_24h': float(market_data.volume_24h_base),
            'market_cap': float(market_data.market_cap),
            'circulating_supply': market_data.circulating_supply,
            'total_supply': market_data.total_supply,
            'rsi_14': rsi,
            'ma_50': ma_50,
            'ma_200': ma_200,
            'last_updated': market_data.last_updated,
            # Additional metrics can be added below
            'market_cap_rank': market_data.market_cap_rank,
            'high_24h': float(market_data.high_24h),
            'low_24h': float(market_data.low_24h),
        }

    def calculate_rsi(self, coin_symbol, market, period=14):
        """Calculate Relative Strength Index for the specified market"""
        historical = MarketData.objects.filter(
            coin_id=coin_symbol,
            market=market
        ).order_by('last_updated')

        prices = [h.price for h in historical]
        if len(prices) < period + 1:
            return 0

        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period-1) + gains[i]) / period
            avg_loss = (avg_loss * (period-1) + losses[i]) / period

        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def calculate_ma(self, coin_symbol, market, window):
        """Calculate Moving Average for the specified market"""
        historical = MarketData.objects.filter(
            coin_id=coin_symbol,
            market=market
        ).order_by('-last_updated')[:window]

        if len(historical) < window:
            return 0.0

        return sum([h.price for h in historical]) / window

    def close_trade(self, trade_id):
        """Execute sell order and update trade record"""
        try:
            with transaction.atomic():
                trade = Trades.objects.select_for_update().get(pk=trade_id)
                if trade.status != 'OPEN':
                    print(f"Trade {trade_id} is not open")
                    return None

                # Execute sell order through Jupiter
                updated_trade = self.execution_handler.execute_sell_order(trade)
                print(f"Successfully sold {trade.quantity} {trade.coin_id}")
                return updated_trade
        except Exception as e:
            print(f"Failed to sell {trade.coin_id}: {e}")
            return None

    def register_trade(self, coin):
        """Execute buy order and create trade record"""
        try:
            # Execute buy order through Jupiter
            trade = self.execution_handler.execute_buy_order(
                coin_symbol=coin.coin_symbol,
                usd_amount=self.usd_amount_per_trade
            )

            print(f"Successfully bought {trade.quantity} {coin.coin_symbol}")
            return trade
        except Exception as e:
            print(f"Failed to buy {coin.coin_symbol}: {e}")
            return None

    def update_trade(self, trade_id):
        """Update trade parameters based on market conditions"""
        try:
            trade = Trades.objects.get(pk=trade_id)
            trade.status = "HOLD"
            trade.save()
            return True
        except Exception as e:
            print(f"Failed to update trade: {e}")
            return None


    def execute_trading_cycle(self):
        """Enhanced trading cycle with proper error handling"""
        try:
            print("Ingesting data...")
            self.ingest_all_data()
            print("Data ingested successfully.")
            newest_coins = self.get_newest_coins()
            active_trades = Trades.objects.filter(status='OPEN')

            # Process existing trades first
            for trade in active_trades:
                insights = self.get_coin_insights(trade.coin_id)
                evaluation = self.filtering_algorithm.evaluate_coin(insights)
                
                for trade_eval in evaluation.get("trades", []):
                    if trade_eval["action"] == "SELL":
                        self.close_trade(trade_eval["id"])
                    elif trade_eval["action"] == "HOLD":
                        self.update_trade(trade_eval["id"])

            # Process new buy opportunities
            buy_candidates = []
            for coin in newest_coins:
                insights = self.get_coin_insights(coin.coin_symbol)
                evaluation = self.filtering_algorithm.evaluate_coin(insights)

                print(f"Evaluation for {coin.coin_symbol}: {evaluation}")

                if evaluation["ready_to_buy"]:
                    buy_candidates.append((coin, evaluation["buy_score"]))

            # Execute top 3 buy candidates sorted by score
            for coin, _ in sorted(buy_candidates, key=lambda x: x[1], reverse=True)[:3]:
                existing = Trades.objects.filter(coin_id=coin.coin_symbol, status='OPEN')
                if not existing.exists():  # Prevent duplicate positions
                    self.register_trade(coin)

            print("Trading cycle completed successfully")
        except Exception as e:
            print(f"Error in trading cycle: {e}")
        finally:
            time.sleep(60 * self.trading_cycle)
