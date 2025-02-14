from django.shortcuts import render
from .trading_bot import TradingBot
from django.http import HttpResponse
from .models import Trades
# Create your views here.
# from meme_coin_trading_bot.trading_bot.ingest_handler import main

def index(request):
    trading_bot = TradingBot()
    trading_bot.execute_trading_cycle()
    word = "Execute Trading Cycle Started"
    return HttpResponse(word)

def home(request):
    all_trades = Trades.objects.all()
    return render(request,'home.html', context={'all_trades':all_trades})
