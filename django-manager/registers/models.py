from django.db import models

from djmoney.models.fields import MoneyField


class Product(models.Model):
    """
    Product model that configures the list of available
    products in the POS application. It includes all
    elements that are required to print a recipe if an
    item is bought.
    """
    name = models.CharField(max_length=100)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')
    icon = models.ImageField(blank=True, null=True)

    def __str__(self):
        return '{} ({})'.format(self.name, self.price)
