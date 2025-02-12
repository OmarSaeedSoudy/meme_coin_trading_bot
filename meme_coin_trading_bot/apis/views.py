from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from trading_bot.models import Token, MarketData, Wallet, Trade, Portfolio, Alert, Analytics
from .serializers import TokenSerializer, MarketDataSerializer, WalletSerializer, TradeSerializer, PortfolioSerializer, AlertSerializer, AnalyticsSerializer

class TokenViewSet(viewsets.ModelViewSet):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer

class MarketDataViewSet(viewsets.ModelViewSet):
    queryset = MarketData.objects.all()
    serializer_class = MarketDataSerializer

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer

class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

class AnalyticsViewSet(viewsets.ModelViewSet):
    queryset = Analytics.objects.all()
    serializer_class = AnalyticsSerializer

@api_view(['GET'])
def business_overview(request):
    total_tokens = Token.objects.count()
    total_trades = Trade.objects.count()
    total_wallets = Wallet.objects.count()

    data = {
        "total_tokens": total_tokens,
        "total_trades": total_trades,
        "total_wallets": total_wallets
    }
    return Response(data)
