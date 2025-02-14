# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoriesViewSet)
router.register(r'memecoins', views.MemeCoinsViewSet)
router.register(r'memecoin-categories', views.MemeCoinCategoriesViewSet)
router.register(r'marketdata', views.MarketDataViewSet)
router.register(r'trades', views.TradesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('execute-buy/', views.TradesViewSet.as_view({'post': 'execute_buy'})),
    path('execute-sell/<int:pk>/', views.TradesViewSet.as_view({'post': 'execute_sell'})),
]