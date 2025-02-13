from django.db.models import Sum, F
from .models import Trade

class PositionTracker:
    @staticmethod
    def get_open_position(coin):
        return Trade.objects.filter(
            coin=coin,
            trade_type=Trade.BUY,
            related_trade__isnull=True
        ).aggregate(
            total_quantity=Sum('quantity'),
            average_price=Sum(F('quantity') * F('price')) / Sum('quantity')
        )

    @staticmethod
    def calculate_unrealized_pl(coin, current_price):
        position = PositionTracker.get_open_position(coin)
        if position['total_quantity']:
            return (current_price - position['average_price']) * position['total_quantity']
        return 0