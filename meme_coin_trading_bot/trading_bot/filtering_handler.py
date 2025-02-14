from django.utils import timezone
from .models import Trades  

class FilteringAlgorithm:
    def __init__(self):
        self.profit_target = 0.02  # 2% profit target
        self.stop_loss_percent = -0.01  # 1% stop loss
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        self.volume_threshold = 1000000  # Minimum volume threshold in base currency

    def evaluate_coin(self, coin_insights):
        """Main evaluation function returning decision"""
        coin_results = {}

        # Boolean to Check if coin is ready to be bought
        buy_decision, buy_score, buy_reasons = self._evaluate_buy(coin_insights)
        coin_results["ready_to_buy"] = buy_decision
        coin_results["buy_reasons"] = buy_reasons
        coin_results["buy_score"] = buy_score

        # Check if coin trades are ready to be closed
        coin_results["trades"] = []
        # get all coin trades 
        all_trades = Trades.objects.filter(coin_id=coin_insights['symbol'], status='OPEN')
        for trade in all_trades:
            action, profit, sell_reasons = self._evaluate_sell(coin_insights, trade)
            coin_results["trades"].append({
                "id": trade.id,
                "action": action,
                "profit": profit
            })

        return coin_results


    def _evaluate_buy(self, insights):
        """Evaluate buy conditions"""
        reasons = []
        buy_score = 0

        # Technical indicators
        if insights.get('rsi_14', 0) < self.rsi_oversold:
            reasons.append('Oversold (RSI < 30)')
            buy_score += 1

        if insights['price'] > insights['ma_50']:
            reasons.append('Price above 50-day MA')
            buy_score += 1
        if insights.get('ma_50') > insights['ma_200']:
            reasons.append('Golden Cross (50MA > 200MA)')
            buy_score += 1

        # Fundamental metrics
        if insights.get('volume_24h', 0) > self.volume_threshold:
            reasons.append('High trading volume')
            buy_score += 1

        # Price momentum
        if all([
            insights['price_change_1h'] > 0,
            insights['price_change_24h'] > 0
        ]):
            reasons.append('Positive momentum across all timeframes')
            buy_score += 1

        return buy_score >= 3, buy_score, reasons
    


    def _evaluate_sell(self, insights, trade):
        """Evaluate sell conditions"""
        reasons = []
        sell_score = 0

        # Calculate position performance
        current_price = insights['price']
        bought_price = trade.buying_price
        price_change = (current_price - bought_price) / bought_price

        # Profit/Loss conditions
        if price_change >= self.profit_target:
            reasons.append(f"Hit profit target (+{price_change:.2%})")
            sell_score += 1
        if price_change <= self.stop_loss_percent:
            reasons.append(f"Hit stop loss ({price_change:.2%})")
            sell_score += 1

        # Technical indicators
        if insights['rsi_14'] > self.rsi_overbought:
            reasons.append('Overbought (RSI > 70)')
            sell_score += 1
        if insights['price'] < insights['ma_200']:
            reasons.append('Price below 200-day MA')
            sell_score += 1

        # Time-based exit
        if (timezone.now() - trade.bought_at).days > 7:
            reasons.append('Held longer than 7 days')
            sell_score += 1

        # Volume drying up
        if insights['volume_24h'] < (self.volume_threshold * 0.5):
            reasons.append('Low trading volume')
            sell_score += 1

        profit = insights['price'] * self.profit_target

        return 'sell' if sell_score >= 3 else 'hold', profit, reasons