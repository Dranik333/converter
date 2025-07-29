from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import requests

API_KEY = '22a140aff796a3b025850c5a'  # твой ключ exchangerate-api.com

# Словарь с русскими краткими названиями валют
RUSSIAN_CURRENCY_NAMES = {
    'USD': 'Доллар',
    'EUR': 'Евро',
    'RUB': 'Рубль',
    'GBP': 'Фунт',
    'JPY': 'Йена',
    'CNY': 'Юань',
    'AUD': 'Австралийский доллар',
    'CAD': 'Канадский доллар',
    'CHF': 'Швейцарский франк',
    'HKD': 'Гонконгский доллар',
    'NZD': 'Новозеландский доллар',
    'SEK': 'Шведская крона',
    'KRW': 'Вона',
    'SGD': 'Сингапурский доллар',
    'NOK': 'Норвежская крона',
    'MXN': 'Мексиканское песо',
    'INR': 'Индийская рупия',
    'BRL': 'Бразильский реал',
    'ZAR': 'Южноафриканский ранд',
    # Добавь остальные, которые хочешь
}

@csrf_exempt
def currency_converter(request):
    currencies = []
    error = None
    result = None
    history = request.session.get('history', [])
    rates_cache = request.session.get('rates_cache', {})
    rates_updated = request.session.get('rates_updated')

    def is_cache_valid():
        if not rates_updated:
            return False
        updated_time = datetime.strptime(rates_updated, '%Y-%m-%d %H:%M:%S')
        return datetime.now() - updated_time < timedelta(minutes=10)  # кэш живёт 10 минут

    # Получаем список валют из API (кэшируем в сессии)
    if 'currencies_list' in request.session:
        currencies = request.session['currencies_list']
    else:
        try:
            url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/codes"
            response = requests.get(url)
            data = response.json()
            if data['result'] == 'success':
                currencies = []
                for code, name in data['supported_codes']:
                    short_name = RUSSIAN_CURRENCY_NAMES.get(code, name)
                    currencies.append({'code': code, 'name': name, 'short_name': short_name})
                request.session['currencies_list'] = currencies
            else:
                error = "Не удалось получить список валют с API."
        except Exception as e:
            error = f"Ошибка при получении списка валют: {e}"

    valid_codes = [c['code'] for c in currencies]

    if request.method == "POST" and not error:
        amount = request.POST.get('amount')
        from_currency = request.POST.get('from_currency')
        to_currency = request.POST.get('to_currency')
        commission = request.POST.get('commission', '0')

        # Валидация суммы
        try:
            amount = float(amount.replace(',', '.'))
            if amount <= 0:
                raise ValueError
        except:
            error = "Введите корректную сумму (число больше 0)"

        # Валидация комиссии
        if not error:
            try:
                commission = commission.replace(',', '.').strip()
                if commission == '':
                    commission = 0.0
                else:
                    commission = float(commission)
                if commission < 0:
                    raise ValueError
            except ValueError:
                error = "Введите корректную комиссию (число 0 или больше, может быть дробным)"

        # Валидация валют
        if not error:
            if from_currency not in valid_codes or to_currency not in valid_codes:
                error = "Выбрана недопустимая валюта"
            elif from_currency == to_currency:
                error = "Выберите разные валюты для конвертации"

        if not error:
            if is_cache_valid() and rates_cache.get('base') == from_currency:
                rates = rates_cache.get('conversion_rates', {})
            else:
                url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
                try:
                    response = requests.get(url)
                    data = response.json()
                    if data['result'] == 'success':
                        rates = data['conversion_rates']
                        request.session['rates_cache'] = data
                        request.session['rates_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        error = f"Ошибка API: {data.get('error-type', 'неизвестная ошибка')}"
                        rates = {}
                except Exception as e:
                    error = f"Ошибка получения данных с API: {str(e)}"
                    rates = {}

            if not error:
                if to_currency in rates:
                    rate = rates[to_currency]
                    converted = amount * rate
                    converted_with_commission = converted * (1 - commission / 100)
                    result = f"{amount} {from_currency} = {converted_with_commission:.2f} {to_currency} " \
                             f"(курс: {rate:.4f}, комиссия: {commission}%)"

                    history.insert(0, {
                        'datetime': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'from': from_currency,
                        'to': to_currency,
                        'amount': amount,
                        'result': f"{converted_with_commission:.2f}",
                        'commission': commission,
                        'rate': rate,
                    })
                    history = history[:5]
                    request.session['history'] = history
                else:
                    error = "Не удалось получить курс для выбранной валюты"

    context = {
        'currencies': currencies,
        'result': result,
        'error': error,
        'history': history,
    }

    return render(request, 'converter/converter.html', context)


def about(request):
    context = {
        'title': 'О сайте',
        'description': 'Этот сайт создан для удобного конвертирования валют с актуальными курсами. '
                       'Здесь вы можете быстро и удобно конвертировать валюты с учётом комиссии и видеть историю последних операций.',
    }
    return render(request, 'converter/about.html', context)





