from django.db import models
import uuid

class Token(models.Model):
    token_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=20, unique=True)
    contract_address = models.CharField(max_length=255, unique=True)
    creator_wallet = models.CharField(max_length=255)
    launch_date = models.DateTimeField()
    scam_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

class MarketData(models.Model):
    market_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="market_data")
    price_usd = models.DecimalField(max_digits=20, decimal_places=10)
    volume_24h = models.DecimalField(max_digits=20, decimal_places=2)
    liquidity = models.DecimalField(max_digits=20, decimal_places=2)
    market_cap = models.DecimalField(max_digits=20, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

class Wallet(models.Model):
    wallet_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.CharField(max_length=255)
    address = models.CharField(max_length=255, unique=True)
    balance_sol = models.DecimalField(max_digits=20, decimal_places=10, default=0.0)
    balance_usd = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    last_sync = models.DateTimeField(auto_now=True)

class Trade(models.Model):
    TRADE_TYPES = [('BUY', 'Buy'), ('SELL', 'Sell')]
    STATUS_TYPES = [('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')]

    trade_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="trades")
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="trades")
    order_type = models.CharField(max_length=10, choices=TRADE_TYPES)
    order_status = models.CharField(max_length=15, choices=STATUS_TYPES, default="PENDING")
    price = models.DecimalField(max_digits=20, decimal_places=10)
    amount = models.DecimalField(max_digits=20, decimal_places=5)
    tx_hash = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Portfolio(models.Model):
    portfolio_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="portfolio")
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="portfolio")
    quantity = models.DecimalField(max_digits=20, decimal_places=5)
    avg_price = models.DecimalField(max_digits=20, decimal_places=10)
    pnl = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

class Alert(models.Model):
    ALERT_TYPES = [('EMAIL', 'Email'), ('SMS', 'SMS'), ('WEBHOOK', 'Webhook')]

    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="alerts")
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="alerts")
    condition = models.TextField()
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

class Analytics(models.Model):
    TIME_WINDOWS = [('1H', '1 Hour'), ('24H', '24 Hours'), ('7D', '7 Days'), ('30D', '30 Days')]

    analytics_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="analytics")
    time_window = models.CharField(max_length=10, choices=TIME_WINDOWS)
    avg_price = models.DecimalField(max_digits=20, decimal_places=10)
    avg_volume = models.DecimalField(max_digits=20, decimal_places=2)
    trends = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
