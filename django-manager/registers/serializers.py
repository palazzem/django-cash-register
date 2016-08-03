from django.db import transaction
from django.conf import settings

from rest_framework import serializers

from djmoney.contrib.django_rest_framework.fields import MoneyField

from .models import Product, Recipe, Sell


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model
    """
    class Meta:
        model = Product


class RecipeItemSerializer(serializers.Serializer):
    """
    The ``RecipeItemSerializer`` serializes a single line
    item of a generic Recipe. Each row must contain:
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
    price = MoneyField(max_digits=10, decimal_places=2)
    price_currency = serializers.ChoiceField(settings.CURRENCIES, default='EUR')
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, default=1.0)


class RecipeSerializer(serializers.Serializer):
    """
    The ``RecipeSerializer`` serializes a list of products
    so that they can be used to create a new recipe. Anyway,
    it will not accept directly a ``Recipe`` model because
    other fields should not be set by the user input.

    This serializer creates a new ``Recipe`` and then all
    related ``Sell`` instances. Furthermore, it ensures
    that the given input is also validated for the
    ``python-cash-register`` package
    """
    products = RecipeItemSerializer(many=True, allow_empty=False)

    @transaction.atomic
    def save(self):
        """
        Custom save() for serializer that creates the ``Recipe``, honoring
        the ManyToMany relationship with ``Product`` (through the ``Sell``
        model).

        The creation pass through the following steps:
            * a transaction is created
            * the ``Recipe`` is created
            * for each product in ``products``, create a ``Sell`` relationship
              with ``Product``
            * if the result is GOOD => commit the transaction
            * if the result is BAD => rollback the transaction
        """
        # create an empty Recipe
        recipe = Recipe.objects.create()
        # add sold items to the Recipe
        for item in self.validated_data['products']:
            sell = Sell(
                recipe=recipe,
                product=item['id'],
                quantity=item['quantity'],
                price=item['price'],
                price_currency=item['price_currency'],
            )
            sell.save()
