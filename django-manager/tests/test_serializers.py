import pytest

from model_mommy import mommy

from registers.models import Product
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
        Test the ``RecipeSerializer`` so that a list of products creates a new
        ``Recipe`` object with bought items:
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
        Ensure that the ``RecipeSerializer`` doesn't create a ``Recipe`` object
        if the list of products is empty.
        """
        # use the serializer with an empty list of products
        recipe = {
            'products': []
        }
        # check the serializer
        serializer = RecipeSerializer(data=recipe)
        assert serializer.is_valid() is False
        assert serializer.errors['products']['non_field_errors'][0] == 'This list may not be empty.'
