from django.db import models
from django.utils import formats

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


class Recipe(models.Model):
    """
    Recipe model that aggregates a set of products and that
    creates the proper commands to print the Recipe.
    """
    date = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField('Product', through='Sell')

    def __str__(self):
        return formats.date_format(self.date, 'DATETIME_FORMAT')


class Sell(models.Model):
    """
    ManyToMany relationship that includes all extra fields
    for the Recipe-Product relation. It provides:
        * the quantity of sold items
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')

    def __str__(self):
        return '{}x{} sold {}'.format(self.product, self.quantity, self.recipe)
