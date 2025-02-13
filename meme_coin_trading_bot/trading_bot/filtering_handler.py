from django.db.models import F, Window
from django.db.models.functions import Lag
from .models import MarketData, MemeCoins, Trade
import numpy as np
from django.db.models import Sum, F

class MemeCoinFilter:
    ESSENTIAL_KEYS = {
        'current_price',
        'price_change_24h',
        'price_change_percentage_24h',
        'market_cap',
        'total_volume',
        'high_24h',
        'low_24h',
        'circulating_supply',
        'ath',
        'ath_change_percentage'
    }

    @staticmethod
    def filter_essential(data):
        """Filter only essential trading metrics from MarketData instance"""
        return {
            key: getattr(data, key)
            for key in MemeCoinFilter.ESSENTIAL_KEYS
            if hasattr(data, key)
        }

    @classmethod
    def calculate_technical_indicators(cls, coin):
        """Calculate technical indicators using historical MarketData"""
        historical_data = MarketData.objects.filter(coin=coin).order_by('-timestamp')[:200]

        if len(historical_data) < 50:
            return None

        prices = [float(data.current_price) for data in historical_data]
        volumes = [float(data.total_volume) for data in historical_data]

        return {
            'sma_50': cls._calculate_sma(prices, 50),
            'sma_200': cls._calculate_sma(prices, 200),
            'rsi': cls._calculate_rsi([data.price_change_percentage_24h for data in historical_data]),
            'volume_ma': cls._calculate_sma(volumes, 20),
            'price_volatility': cls._calculate_volatility(historical_data)
        }

    @staticmethod
    def _calculate_sma(data, window):
        return np.mean(data[-window:]) if len(data) >= window else None

    @staticmethod
    def _calculate_rsi(price_changes, period=14):
        if len(price_changes) < period:
            return 50  # Neutral value for insufficient data

        gains = [x for x in price_changes[-period:] if x > 0]
        losses = [abs(x) for x in price_changes[-period:] if x < 0]

        avg_gain = np.mean(gains) if gains else 0
        avg_loss = np.mean(losses) if losses else 1e-9  # Avoid division by zero

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def _calculate_volatility(historical_data):
        """Calculate volatility using last 24h data"""
        if not historical_data:
            return 0

        latest = historical_data[0]
        return ((latest.high_24h - latest.low_24h) / latest.low_24h) * 100

class TradingDecisionEngine:


    @staticmethod
    def get_average_buy_price(coin):
        """Calculate average price of all unconverted buy positions"""
        buys = Trade.objects.filter(
            coin=coin,
            trade_type=Trade.BUY,
            related_trade__isnull=True
        ).aggregate(
            total_quantity=Sum('quantity'),
            total_cost=Sum(F('quantity') * F('price'))
        )

        if buys['total_quantity'] and buys['total_quantity'] > 0:
            return buys['total_cost'] / buys['total_quantity']
        return None



    @staticmethod
    def make_decision(coin):
        """Main decision-making method using current market data"""
        try:
            latest_data = MarketData.objects.filter(coin=coin).latest('timestamp')
        except MarketData.DoesNotExist:
            return 'HOLD'

        filtered_data = MemeCoinFilter.filter_essential(latest_data)
        technicals = MemeCoinFilter.calculate_technical_indicators(coin)

        if not technicals:
            return 'HOLD'

        decision_data = {**filtered_data, **technicals}
        decision_data['price_volatility'] = technicals['price_volatility']

        if TradingDecisionEngine._should_buy(decision_data):
            return 'BUY'
        if TradingDecisionEngine._should_sell(decision_data, coin):  # Now passing coin parameter
            return 'SELL'
        return 'HOLD'





    @staticmethod
    def should_buy(data):
        buy_conditions = [
            data['price_change_percentage_24h'] > 5,
            data['current_price'] > data['sma_50'],
            data['volume_ma'] > 1.5 * data['total_volume'],
            data['rsi'] < 30,
            data['ath_change_percentage'] < -30
        ]
        return sum(buy_conditions) >= 3




    @staticmethod
    def _should_sell(data, coin):
        current_price = data['current_price']
        sell_conditions = []

        # Get average buy price from trade history
        avg_buy_price = TradingDecisionEngine.get_average_buy_price(coin)

        if avg_buy_price:
            # Calculate profit/loss percentage
            pl_percent = ((current_price - avg_buy_price) / avg_buy_price) * 100

            # Add profit-based sell conditions
            sell_conditions.extend([
                pl_percent >= 10,  # Take profit at 10%
                pl_percent <= -5,  # Stop loss at -5%
                data['rsi'] > 70,
                data['price_volatility'] > 15,
                current_price >= (0.7 * float(data['ath']))
            ])
        else:
            # No existing position - use technical only
            sell_conditions = [
                data['price_change_percentage_24h'] < -3,
                data['rsi'] > 70,
                data['current_price'] < data['sma_50']
            ]

        return sum(sell_conditions) >= 2