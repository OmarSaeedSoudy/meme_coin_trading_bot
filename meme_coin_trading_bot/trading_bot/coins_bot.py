from .models import MemeCoins, MarketData, Trade
from .filtering_handler import TradingDecisionEngine
from django.db.models import Sum, F

def trading_decision(coin):
    return TradingDecisionEngine.make_decision(coin)

def execute_trading_cycle():
    """Execute pending trades through exchange API"""
    coins = MemeCoins.objects.all()

    for coin in coins:
        decision = trading_decision(coin)
        latest_data = MarketData.objects.filter(coin=coin).latest('timestamp')

        if decision == 'BUY':
            # Implement your buy logic here
            Trade.objects.create(
                coin=coin,
                trade_type=Trade.BUY,
                price=latest_data.current_price,
                quantity=calculate_position_size()  # Implement your position sizing
            )
        elif decision == 'SELL':
            # Get all unconverted buy positions
            buy_trades = Trade.objects.filter(
                coin=coin,
                trade_type=Trade.BUY,
                related_trade__isnull=True
            )

            # Implement your sell logic here
            sell_trade = Trade.objects.create(
                coin=coin,
                trade_type=Trade.SELL,
                price=latest_data.current_price,
                quantity=buy_trades.aggregate(Sum('quantity'))['quantity__sum']
            )

            # Link sell trade to buy trades
            buy_trades.update(related_trade=sell_trade)

if __name__ == "__main__":
    execute_trading_cycle()