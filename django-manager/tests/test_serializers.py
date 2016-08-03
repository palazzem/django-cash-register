import pytest

from decimal import Decimal as D

from model_mommy import mommy

from registers.models import Product, Recipe
from registers.serializers import ProductSerializer, RecipeItemSerializer, RecipeSerializer


class TestProduct:
    def test_serializer(self, temp_image):
        """
        Test the ``Product`` serializer
        """
        # a product
        product = {
            'id': 1,
            'name': 'Croissant',
            'default_price': '5.90',
            'default_price_currency': 'EUR',
            'icon': temp_image,
        }
        # check the serializer
        serializer = ProductSerializer(data=product)
        assert serializer.is_valid() is True

    def test_optional_fields(self):
        """
        Test the ``Product`` serializer optinal fields:
            * default_price_currency, defaults to 'EUR'
            * icon is not mandatory
        """
        # a product without image
        product = {
            'id': 1,
            'name': 'Croissant',
            'default_price': '5.90',
        }
        # check the serializer
        serializer = ProductSerializer(data=product)
        assert serializer.is_valid() is True


class TestRecipe:
    @pytest.mark.django_db
    def test_item_serializer(self):
        """
        Test the ``RecipeItemSerializer``; it doesn't contain
        the ``description`` field, even if it's required to
        print a valid invoice
        """
        # a product
        product = mommy.make(Product)
        # a serialized item
        item = {
            'id': product.id,
            'price': '5.90',
            'price_currency': 'EUR',
            'quantity': '10.0',
        }
        # check the serializer
        serializer = RecipeItemSerializer(data=item)
        assert serializer.is_valid() is True

    @pytest.mark.django_db
    def test_item_serializer_defaults(self):
        """
        Test the ``RecipeItemSerializer`` optional attributes
        and defaults
        """
        # a product
        product = mommy.make(Product)
        # a serialized item
        item = {
            'id': product.id,
            'price': '5.90',
        }
        # check the serializer
        serializer = RecipeItemSerializer(data=item)
        assert serializer.is_valid() is True
        assert serializer.validated_data['price_currency'] == 'EUR'
        assert serializer.validated_data['quantity'] == 1.0

    @pytest.mark.django_db
    def test_item_serializer_wrong_currency(self):
        """
        Test the ``RecipeItemSerializer`` with a wrong / not supported currency
        """
        # a product
        product = mommy.make(Product)
        # a serialized item
        item = {
            'id': product.id,
            'price': '5.90',
            'price_currency': 'USD',
        }
        # check the serializer
        serializer = RecipeItemSerializer(data=item)
        assert serializer.is_valid() is False
        assert len(serializer.errors) == 1
        assert serializer.errors['price_currency'][0] == '"USD" is not a valid choice.'

    @pytest.mark.django_db
    def test_recipe_serializer(self):
        """
        Test the ``RecipeSerializer`` so that a list of products in a ``Recipe``
        instance are allowed:
            * create 3 random products
            * sell each product using different prices and quantities
            * the serializer must be valid
        """
        # a list of product
        products = mommy.make(Product, _quantity=3)
        # products that are sold
        recipe = {
            'products': [
                {
                    'id': products[0].id,
                    'price': '5.90',
                },
                {
                    'id': products[1].id,
                    'price': '2.00',
                    'quantity': '2.0',
                },
                {
                    'id': products[2].id,
                    'price': '1.00',
                    'quantity': '1.68',
                },
            ]
        }
        # check the serializer
        serializer = RecipeSerializer(data=recipe)
        assert serializer.is_valid() is True

    @pytest.mark.django_db
    def test_recipe_serializer_empty_list(self):
        """
        Ensure that the ``RecipeSerializer`` isn't valid if the
        list of products is empty.
        """
        # use the serializer with an empty list of products
        recipe = {
            'products': []
        }
        # check the serializer
        serializer = RecipeSerializer(data=recipe)
        assert serializer.is_valid() is False
        assert serializer.errors['products']['non_field_errors'][0] == 'This list may not be empty.'

    @pytest.mark.django_db
    def test_recipe_serializer_save(self):
        """
        Test the ``RecipeSerializer`` so that a list of products creates a new
        ``Recipe`` object with bought items:
            * create 3 random products
            * sell each product using different prices and quantities
            * the serializer must be saved
            * the Recipe must be created
            * each row of the recipe must be saved
        """
        # a list of product
        products = mommy.make(Product, _quantity=3)
        # products that are sold
        recipe = {
            'products': [
                {
                    'id': products[0].id,
                    'price': '5.90',
                },
                {
                    'id': products[1].id,
                    'price': '2.00',
                    'quantity': '2.0',
                },
                {
                    'id': products[2].id,
                    'price': '1.00',
                    'quantity': '1.68',
                },
            ]
        }
        # check the serializer
        serializer = RecipeSerializer(data=recipe)
        # save the serializer
        serializer.is_valid()
        serializer.save()
        # database checks
        assert Recipe.objects.count() == 1
        recipe = Recipe.objects.all()[0]
        assert recipe.products.count() == 3
        # products exists with the proper quantities and prices
        sold_items = recipe.products.through.objects.all()
        assert sold_items[0].product_id == products[0].id
        assert sold_items[0].quantity == D('1.0')
        assert sold_items[0].price.amount == D('5.90')
        assert sold_items[1].product_id == products[1].id
        assert sold_items[1].quantity == D('2.0')
        assert sold_items[1].price.amount == D('2.00')
        assert sold_items[2].product_id == products[2].id
        assert sold_items[2].quantity == D('1.68')
        assert sold_items[2].price.amount == D('1.00')

    @pytest.mark.django_db
    def test_recipe_serializer_save_rollback(self):
        """
        Ensure that ``RecipeSerializer`` does a rollback if something goes
        wrong during the ``Recipe`` creation. This tests raises an exception
        because the save() method cannot be called before is_valid(); even
        if the tests seems not related with the bug, it represents just a misuse
        of the serializer that can cause database integrity errors.

        The steps are:
            * sell a fake product that is not available
            * the serializer is saved without validation
            * the Recipe is created but:
                * the ``validated_data`` is not accessible
                * Django does a rollback
            * No recipe must be saved because of the rollback
            * No product must be saved because of the rollback
        """
        # product with a fake item not present in the database
        recipe = {
            'products': [
                {
                    'id': 1,
                    'price': '5.90',
                },
            ]
        }
        # check the serializer
        serializer = RecipeSerializer(data=recipe)
        # save the serializer but expect a DRF ``AssertionError``
        with pytest.raises(AssertionError):
            serializer.save()
        # the Recipe must not be created
        assert Recipe.objects.count() == 0
        assert Product.objects.count() == 0
