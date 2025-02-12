# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import (
#     TokenViewSet, MarketDataViewSet, WalletViewSet, TradeViewSet, 
#     PortfolioViewSet, AlertViewSet, AnalyticsViewSet, business_overview
# )

# router = DefaultRouter()
# router.register(r'tokens', TokenViewSet)
# router.register(r'market-data', MarketDataViewSet)
# router.register(r'wallets', WalletViewSet)
# router.register(r'trades', TradeViewSet)
# router.register(r'portfolio', PortfolioViewSet)
# router.register(r'alerts', AlertViewSet)
# router.register(r'analytics', AnalyticsViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
#     path('api/business-overview/', business_overview, name='business-overview'),
# ]
