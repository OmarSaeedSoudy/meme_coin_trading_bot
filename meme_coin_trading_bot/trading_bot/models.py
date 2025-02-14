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
    coin_name = models.CharField(max_length=255, null=True)
    coin_full_name = models.CharField(max_length=255, null=True)
    coin_symbol = models.CharField(max_length=10, null=True)
    coin_description = models.TextField(null=True)
    total_coins_mined = models.BigIntegerField(null=True)
    coin_creation_date = models.DateTimeField(null=True)
    inserted_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.coin_name}"
    

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
    coin_id = models.CharField(max_length=100, unique=False)
    market = models.CharField(max_length=100, null=True)  # RAW.MARKET
    last_updated = models.DateTimeField(null=True)  # From RAW.LASTUPDATE

    # Price data
    price = models.DecimalField(max_digits=30, decimal_places=15)  # RAW.PRICE
    currency = models.CharField(max_length=5, default="USD")  # RAW.TOSYMBOL
    high_24h = models.DecimalField(max_digits=30, decimal_places=15, null=True, default=0)  # RAW.HIGH24HOUR
    low_24h = models.DecimalField(max_digits=30, decimal_places=15, null=True, default=0)  # RAW.LOW24HOUR
    open_24h = models.DecimalField(max_digits=30, decimal_places=15, null=True, default=0)  # RAW.OPEN24HOUR

    # Volume metrics
    last_volume_base = models.DecimalField(max_digits=30, decimal_places=15, null=True, default=0)  # RAW.LASTVOLUME
    last_volume_quote = models.DecimalField(max_digits=30, decimal_places=15, null=True, default=0)  # RAW.LASTVOLUMETO
    volume_24h_base = models.DecimalField(max_digits=30, decimal_places=15, null=True, default=0)  # RAW.VOLUME24HOUR
    volume_24h_quote = models.DecimalField(max_digits=30, decimal_places=15, null=True, default=0)  # RAW.VOLUME24HOURTO

    # Market dynamics
    price_change_percentage_1h = models.DecimalField(max_digits=10, decimal_places=5, null=True, default=0)  # RAW.CHANGEPCTHOUR
    price_change_percentage_24h = models.DecimalField(max_digits=10, decimal_places=5, null=True, default=0)  # RAW.CHANGEPCT24HOUR
    price_change_percentage_7d = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)

    # Supply metrics
    circulating_supply = models.BigIntegerField()  # RAW.CIRCULATINGSUPPLY
    total_supply = models.BigIntegerField(null=True, blank=True)  # RAW.SUPPLY

    # Market capitalization
    market_cap = models.DecimalField(max_digits=30, decimal_places=15, null=True, default=0)  # RAW.MKTCAP or calculated
    market_cap_rank = models.PositiveIntegerField(null=True, blank=True)

    # Liquidity metrics
    bid_ask_spread = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, default=0)
    liquidity_score = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, default=0)

    # Conversion info
    conversion_type = models.CharField(max_length=20, null=True, blank=True)  # RAW.CONVERSIONTYPE
    conversion_symbol = models.CharField(max_length=10, null=True, blank=True)  # RAW.CONVERSIONSYMBOL

    # Timestamps
    inserted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-last_updated']),
            models.Index(fields=['market_cap']),
            models.Index(fields=['price_change_percentage_24h']),
        ]
        ordering = ['-last_updated']





class Trades(models.Model):
    TRADE_TYPES = ("BUY", "SELL", "HOLD")
    STATUS_TYPES = ("OPEN", "CLOSED")


    # Trade Identification
    trade_id = models.AutoField(primary_key=True)
    coin_id = models.CharField(max_length=10, default='SOL')  # Fixed as SOL
    trade_type = models.CharField(max_length=4, null=True)
    status = models.CharField(max_length=6, null=True, default='OPEN')

    # Pricing Information
    buying_price = models.DecimalField(max_digits=30, decimal_places=15)  # Buy price
    selling_price = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)  # Sell price
    quantity = models.DecimalField(max_digits=30, decimal_places=15)  # Quantity
    # network_fee = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True) # Network fee 
    total_paid_amount = models.DecimalField(max_digits=30, decimal_places=15)  # Total paid amount buying_price * quantity
    total_received_amount = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)  # Total received amount selling_price * quantity

    # Timing Information
    buy_date = models.DateTimeField(auto_now_add=True)
    sell_date = models.DateTimeField(null=True, blank=True)


    # Blockchain Specific Fields
    tx_hash = models.CharField(max_length=100, unique=True)  # Solana transaction hash
    wallet_address = models.CharField(max_length=44)  # Solana wallet address
    token_address = models.CharField(max_length=44, default='So11111111111111111111111111111111111111112')  # SOL mint address

    def __str__(self):
        return f"{self.coin_id} | {self.trade_type} | {self.status} | {self.buy_date}"
