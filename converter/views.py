from django.shortcuts import render
from django.shortcuts import render
import requests

def index(request):
    # твой код обработки запроса и вывода шаблона
    return render(request, 'converter/index.html', {})
from django.shortcuts import render
import requests

API_URL = "https://open.er-api.com/v6/latest/USD"

def get_rates():
    response = requests.get(API_URL)
    data = response.json()
    if data['result'] == 'success':
        return data['rates']
    return {}

def convert_currency(amount, from_currency, to_currency, rates):
    if from_currency == 'USD':
        base_amount = amount
    else:
        base_amount = amount / rates.get(from_currency, 1)
    converted = base_amount * rates.get(to_currency, 1)
    return round(converted, 4)

def index(request):
    rates = get_rates()
    currencies = sorted(rates.keys())
    result = None
    error = None

    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            from_currency = request.POST.get('from_currency')
            to_currency = request.POST.get('to_currency')

            if from_currency not in rates or to_currency not in rates:
                error = "Выберите корректные валюты."
            else:
                converted_amount = convert_currency(amount, from_currency, to_currency, rates)
                result = f"{amount} {from_currency} = {converted_amount} {to_currency}"

        except (ValueError, TypeError):
            error = "Введите корректное число."

    return render(request, 'converter/index.html', {
        'currencies': currencies,
        'result': result,
        'error': error,
    })


# Create your views here.
