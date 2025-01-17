from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Order
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q

def delete_order(request, order_id):
    """
    Удаляет заказ по его идентификатору.

    Аргументы:
        request (HttpRequest): HTTP-запрос.
        order_id (int): Идентификатор заказа, который нужно удалить.

    Возвращает:
        HttpResponseRedirect: Перенаправление на список заказов.
    """
    # Находим заказ по ID или возвращаем 404 ошибку
    order = get_object_or_404(Order, id=order_id)
    # Удаляем заказ из базы данных
    order.delete()
    # Перенаправляем на страницу со списком заказов
    return redirect('orders_list')


def add_order(request):
    """
    Добавляет новый заказ в систему.

    Аргументы:
        request (HttpRequest): HTTP-запрос.

    Возвращает:
        HttpResponse или HttpResponseRedirect:
            - Если запрос POST, то редирект на список заказов или ошибка с сообщением.
            - Если запрос GET, возвращает форму для добавления нового заказа.
    """
    if request.method == 'POST':
        # Получаем данные из POST-запроса
        table_number = request.POST.get('table_number')
        items = request.POST.getlist('items[]')
        prices = request.POST.getlist('prices[]')

        # Проверка на корректность данных
        if not table_number or not items or not prices:
            return JsonResponse({'error': 'Некорректные данные'}, status=400)

        # Подготовка данных для сохранения в JSONField (список словарей)
        items_with_prices = [
            {"name": item, "price": float(price)}
            for item, price in zip(items, prices)
        ]

        # Создаём новый заказ в базе данных
        Order.objects.create(
            table_number=table_number,
            items=items_with_prices,
            status='waiting'  # Статус по умолчанию
        )
        # Перенаправляем пользователя на список заказов
        return redirect('orders_list')

    # Если это GET-запрос, то возвращаем страницу с формой для добавления заказа
    return render(request, 'main/add_order.html')


def update_order_status(request, order_id, new_status):
    """
    Обновляет статус заказа по его ID.

    Аргументы:
        request (HttpRequest): HTTP-запрос.
        order_id (int): Идентификатор заказа.
        new_status (str): Новый статус для заказа.

    Возвращает:
        HttpResponseRedirect: Перенаправление на список заказов.
    """
    # Находим заказ по ID или возвращаем 404 ошибку
    order = get_object_or_404(Order, id=order_id)
    # Обновляем статус заказа
    order.status = new_status
    order.save()
    # Перенаправляем на страницу со списком заказов
    return redirect('orders_list')


def calculate_revenue(request):
    """
    Рассчитывает общую выручку от всех оплаченных заказов.

    Аргументы:
        request (HttpRequest): HTTP-запрос.

    Возвращает:
        HttpResponse: Рендерит страницу с суммой выручки.
    """
    # Суммируем цену всех заказов, которые имеют статус "paid"
    revenue = sum(order.total_price for order in Order.objects.filter(status='paid'))
    # Возвращаем страницу с выручкой
    return render(request, 'main/revenue.html', {'revenue': revenue})


def orders_list(request):
    """
    Отображает список всех заказов с возможностью фильтрации по номеру стола и статусу.

    Аргументы:
        request (HttpRequest): HTTP-запрос.

    Возвращает:
        HttpResponse: Рендерит страницу со списком заказов.
    """
    query = request.GET.get('q')  # Получаем строку поиска из параметров GET-запроса
    selected_status = request.GET.get('status')  # Получаем выбранный статус из параметров GET-запроса

    orders = Order.objects.all()  # Получаем все заказы

    # Словарь для маппинга статусов (для перевода статуса с русского на английский)
    STATUS_MAPPING = {
        'Ожидание': 'waiting',
        'Готово': 'ready',
        'Оплачено': 'paid',
    }

    # Если был выбран статус, фильтруем по нему
    if selected_status:
        # Преобразуем выбранный русский статус в английский
        status_value = STATUS_MAPPING.get(selected_status)
        if status_value:
            orders = orders.filter(status=status_value)

    # Если есть поисковой запрос, фильтруем заказы по номеру стола
    if query:
        status_value = STATUS_MAPPING.get(query)
        # Фильтруем заказы по номеру стола или статусу
        orders = orders.filter(
            Q(table_number__icontains=query) | Q(status=status_value) if status_value else Q(
                table_number__icontains=query)
        )

    # Передаем список статусов и выбранный статус в шаблон
    statuses = STATUS_MAPPING.keys()

    return render(request, 'main/orders_list.html', {
        'orders': orders,  # Список заказов
        'query': query,  # Строка поиска
        'statuses': statuses,  # Доступные статусы для фильтрации
        'selected_status': selected_status,  # Выбранный статус в поиске
    })
