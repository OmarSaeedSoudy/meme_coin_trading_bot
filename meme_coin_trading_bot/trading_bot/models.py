from django.db import models


class Categories(models.Model):
    """
    Categories model to store all coins categories
    """
    category_id = models.CharField(max_length=100, unique=True, null=True)  # CoinGecko ID
    category_name = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.category_name}"

class MemeCoins(models.Model):
    """
    MemeCoins model to store meme coins meta data
    """
    coin_id = models.CharField(max_length=100, unique=True, null=True)  # CoinGecko ID
    name = models.CharField(max_length=255, null=True)
    image_url = models.URLField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    inserted_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name}"
    

class MemeCoinCategories(models.Model):
    """
    MemeCategories model to store many to many relationship between meme coins and categories
    """
    category_id = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="meme_categories")
    coin_id = models.ForeignKey(MemeCoins, on_delete=models.CASCADE, related_name="meme_categories")
    inserted_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.coin_id} - {self.category_id}"
    

class MarketData(models.Model):
    coin = models.ForeignKey(MemeCoins, on_delete=models.CASCADE, related_name="market_data")
    timestamp = models.DateTimeField(auto_now_add=True)
    market_cap = models.BigIntegerField()
    total_volume = models.BigIntegerField()
    price = models.DecimalField(max_digits=20, decimal_places=10)
    price_change_1h = models.FloatField()
    price_change_24h = models.FloatField()
    liquidity_score = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']  # Latest data first
    
    def __str__(self):
        return f"{self.coin.symbol} - {self.price} USD ({self.timestamp})"



# class Trade(models.Model):
#     trade_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     coin_id = models.ForeignKey(MemeCoins, on_delete=models.CASCADE, related_name="trades")
#     trade_type = models.CharField(max_length=4)
#     trade_status = models.CharField(max_length=15)
#     price_at_trade = models.DecimalField(max_digits=20, decimal_places=10)
#     quantity = models.DecimalField(max_digits=20, decimal_places=10)


# class Trade(models.Model):
#     TRADE_TYPES = [('BUY', 'Buy'), ('SELL', 'Sell')]
#     STATUS_TYPES = [('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')]

#     trade_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="trades")
#     token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="trades")
#     order_type = models.CharField(max_length=10, choices=TRADE_TYPES)
#     order_status = models.CharField(max_length=15, choices=STATUS_TYPES, default="PENDING")
#     price = models.DecimalField(max_digits=20, decimal_places=10)
#     amount = models.DecimalField(max_digits=20, decimal_places=5)
#     tx_hash = models.CharField(max_length=255, unique=True, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)



# class Trade(models.Model):
#     TRADE_TYPES = (
#         ('BUY', 'Buy'),
#         ('SELL', 'Sell'),
#     )
#     coin = models.ForeignKey(MemeCoin, on_delete=models.CASCADE, related_name="trades")
#     trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
#     price_at_trade = models.DecimalField(max_digits=20, decimal_places=10)
#     quantity = models.DecimalField(max_digits=20, decimal_places=10)
#     executed_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"{self.trade_type} {self.quantity} {self.coin.symbol} at {self.price_at_trade} USD"
    


