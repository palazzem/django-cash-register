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
        Test the ``Product`` serializer
        """
        # a product without image
        product = {
            'id': 1,
            'name': 'Croissant',
            'default_price': '5.90',
            'default_price_currency': 'EUR',
        }
        # check the serializer
        serializer = ProductSerializer(data=product)
        assert serializer.is_valid() is True
