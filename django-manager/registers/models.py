from django.db import models
from django.db.models import Sum, F
from django.utils import formats

from djmoney.models.fields import MoneyField


class Product(models.Model):
    """
    Product model that configures the list of available
    products in the POS application. It includes all
    elements that are required to print a recipe if an
    item is bought.

    The price field is only a default / suggested price that
    is used when creating the relationship with the ``Recipe``
    model.
    """
    name = models.CharField(max_length=100)
    default_price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')
    icon = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Recipe model that aggregates a set of products and that
    creates the proper commands to print the Recipe.
    """
    date = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField('Product', through='Sell', related_name='recipes')

    def __str__(self):
        sells_qs = self.products.through.objects.all()
        total = sells_qs.aggregate(total=Sum(F('price') * F('quantity')))['total']
        total = total if total is not None else 0.0
        date = formats.date_format(self.date, 'DATETIME_FORMAT')
        return "Total: {} -- {}".format(total, date)


class Sell(models.Model):
    """
    ManyToMany relationship that includes all extra fields
    for the Recipe-Product relation. It provides:
        * the recipe foreign key
        * the product foreign key
        * the quantity of sold items
        * the price of sold items

    Price of sold items is written in this relationship because
    the one in the ``Product`` model is just a default / suggested
    price and this one ensures that you can change the price of
    the Product without changing previous recipes.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')

    def __str__(self):
        return 'Sold {} {} for {} each'.format(self.quantity, self.product, self.price)
