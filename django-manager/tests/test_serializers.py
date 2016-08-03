import pytest

from registers.serializers import ProductSerializer


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
