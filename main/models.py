from django.db import models
from django.core.validators import MinValueValidator
from typing import List, Dict
from decimal import Decimal

class Order(models.Model):
    # Номер стола (целое число)
    table_number: int = models.IntegerField("Номер стола")

    # Список блюд (список словарей с полями 'name' и 'price')
    items: List[Dict[str, str]] = models.JSONField("Блюда", default=list)

    # Итоговая сумма (деньги в десятичном формате с двумя знаками после запятой)
    total_price: Decimal = models.DecimalField("Итоговая сумма", max_digits=10, decimal_places=2)

    # Статус заказа (ожидание, готово, оплачено)
    status: str = models.CharField("Статус", max_length=20, choices=[
        ('waiting', 'Ожидание'),
        ('ready', 'Готово'),
        ('paid', 'Оплачено')
    ])

    def save(self, *args, **kwargs) -> None:
        """
        Переопределенный метод сохранения, который вычисляет итоговую сумму заказа
        перед его сохранением в базу данных.

        Аргументы:
            *args: Дополнительные аргументы
            **kwargs: Дополнительные ключевые аргументы

        Возвращает:
            None
        """
        # Расчет итоговой стоимости заказа по всем блюдам
        self.total_price = sum(item['price'] for item in self.items)
        # Вызов родительского метода для сохранения объекта в базе данных
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Строковое представление заказа, которое возвращает текст
        для отображения в интерфейсе (например, "Заказ #1 (Стол 5)").

        Возвращает:
            str: Строковое представление объекта
        """
        return f"Заказ #{self.id} (Стол {self.table_number})"
