# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from trading_bot.models import (
    Categories,
    MemeCoins,
    MemeCoinCategories,
    MarketData,
    Trades
)
from .serializers import (
    CategoriesSerializer,
    MemeCoinsSerializer,
    MemeCoinCategoriesSerializer,
    MarketDataSerializer,
    TradesSerializer
)
from trading_bot.execution_handler import ExecutionHandler  # Assuming you have this
from rest_framework.filters import SearchFilter, OrderingFilter

class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['category_name']
    ordering_fields = ['inserted_at']

class MemeCoinsViewSet(viewsets.ModelViewSet):
    queryset = MemeCoins.objects.all()
    serializer_class = MemeCoinsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['coin_name', 'coin_symbol']
    ordering_fields = ['coin_creation_date', 'inserted_at']

class MemeCoinCategoriesViewSet(viewsets.ModelViewSet):
    queryset = MemeCoinCategories.objects.all()
    serializer_class = MemeCoinCategoriesSerializer

class MarketDataViewSet(viewsets.ModelViewSet):
    queryset = MarketData.objects.all()
    serializer_class = MarketDataSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['coin_id']
    ordering_fields = ['last_updated', 'market_cap']

class TradesViewSet(viewsets.ModelViewSet):
    queryset = Trades.objects.all()
    serializer_class = TradesSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['coin_id', 'tx_hash']
    ordering_fields = ['buy_date', 'sell_date']

    @action(detail=False, methods=['post'])
    def execute_buy(self, request):
        handler = ExecutionHandler()
        try:
            coin_symbol = request.data.get('coin_symbol')
            usd_amount = float(request.data.get('usd_amount'))

            # Execute the trade
            trade = handler.execute_buy_order(coin_symbol, usd_amount)

            # Serialize the response
            serializer = self.get_serializer(trade)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def execute_sell(self, request, pk=None):
        handler = ExecutionHandler()
        try:
            trade = self.get_object()
            updated_trade = handler.execute_sell_order(trade)

            # Serialize the response
            serializer = self.get_serializer(updated_trade)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def open_trades(self, request):
        open_trades = Trades.objects.filter(status='OPEN')
        serializer = self.get_serializer(open_trades, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def closed_trades(self, request):
        closed_trades = Trades.objects.filter(status='CLOSED')
        serializer = self.get_serializer(closed_trades, many=True)
        return Response(serializer.data)