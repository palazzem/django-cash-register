from django.db import models
from django.db.models import Sum, F
from django.utils import formats

from djmoney.models.fields import MoneyField

from .receipts import timezone_now


class Product(models.Model):
    """
    Product model that configures the list of available
    products in the POS application. It includes all
    elements that are required to print a receipt if an
    item is bought.

    The price field is only a default / suggested price that
    is used when creating the relationship with the ``Receipt``
    model.
    """
    name = models.CharField(max_length=100, unique=True)
    default_price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')
    icon = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.name


class Receipt(models.Model):
    """
    ``Receipt`` model that aggregates a set of products and that
    creates the proper commands to print the ``Receipt``.
    """
    date = models.DateTimeField(default=timezone_now, blank=True)
    products = models.ManyToManyField('Product', through='Sell', related_name='receipts')

    def __str__(self):
        total = self.sell_set.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0.0
        date = formats.date_format(self.date, 'DATETIME_FORMAT')
        return "Total: {0:.2f} -- {1}".format(total, date)


class Sell(models.Model):
    """
    ManyToMany relationship that includes all extra fields
    for the Receipt-Product relationship. It provides:
        * the receipt foreign key
        * the product foreign key
        * the quantity of sold items
        * the price of sold items

    Price of sold items is written in this relationship because
    the one in the ``Product`` model is just a default / suggested
    price and this one ensures that you can change the price of
    the Product without changing previous receipts.
    """
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')

    def __str__(self):
        return 'Sold {} {} for {} each'.format(self.quantity, self.product, self.price)

    def save(self, *args, **kwargs):
        """
        At the data-layer, we check if the price of this sold item is 0.00 and,
        if it's the case, we assign the default value available in the `Product`
        relationship.

        NOTE: we do the assumption that selling an item with price 0.00 is invalid.
        """
        # set the default value after the submission
        if self.price.amount.is_zero():
            self.price = self.product.default_price

        # save the item
        super().save(*args, **kwargs)
