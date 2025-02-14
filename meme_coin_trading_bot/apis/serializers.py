# serializers.py
from rest_framework import serializers
from trading_bot.models import (
    Categories,
    MemeCoins,
    MemeCoinCategories,
    MarketData,
    Trades
)

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'

class MemeCoinsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemeCoins
        fields = '__all__'

class MemeCoinCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemeCoinCategories
        fields = '__all__'

class MarketDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketData
        fields = '__all__'
        read_only_fields = ('inserted_at',)

class TradesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trades
        fields = '__all__'
        read_only_fields = ('buy_date', 'sell_date', 'tx_hash')