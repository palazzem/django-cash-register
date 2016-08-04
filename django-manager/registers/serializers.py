from django.db import transaction
from django.conf import settings

from rest_framework import serializers

from .models import Product, Receipt, Sell


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model
    """
    class Meta:
        model = Product


class ReceiptItemSerializer(serializers.Serializer):
    """
    The ``ReceiptItemSerializer`` serializes a single line
    item of a generic ``Receipt``. Each row must contain:
        * ``id``: the product primary key that should exist
          in the database, otherwise it is not valid
        * ``price``: how much is the price of a single item;
          it should NOT be considered as the total amount
          of this row, because the moltiplication is handled
          internally
        * ``quantity``: how many items are bought; the field
          is optional and could be omitted if the quantity
          is one
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_currency = serializers.ChoiceField(settings.CURRENCIES, default='EUR')
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, default=1.0)


class ReceiptSerializer(serializers.Serializer):
    """
    The ``ReceiptSerializer`` serializes a list of products
    so that they can be used to create a new receipt. Anyway,
    it will not accept directly a ``Receipt`` model because
    other fields should not be set by the user input.

    This serializer creates a new ``Receipt`` and then all
    related ``Sell`` instances. Furthermore, it ensures
    that the given input is also validated for the
    ``python-cash-register`` package
    """
    products = ReceiptItemSerializer(many=True, allow_empty=False)

    @transaction.atomic
    def save(self):
        """
        Custom save() for serializer that creates the ``Receipt``, honoring
        the ManyToMany relationship with ``Product`` (through the ``Sell``
        model).

        The creation pass through the following steps:
            * a transaction is created
            * the ``Receipt`` is created
            * for each product in ``products``, create a ``Sell`` relationship
              with ``Product``
            * if the result is GOOD => commit the transaction
            * if the result is BAD => rollback the transaction
        """
        # create an empty Receipt
        receipt = Receipt.objects.create()
        # add sold items to the Receipt
        for item in self.validated_data['products']:
            sell = Sell(
                receipt=receipt,
                product=item['id'],
                quantity=item['quantity'],
                price=item['price'],
                price_currency=item['price_currency'],
            )
            sell.save()
