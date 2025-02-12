from django.shortcuts import render

# Create your views here.
from trading_bot.ingest_handler import main

def index(request):
    main()
    word = "Hello"
    return render(request, 'index.html', {'word': word})
