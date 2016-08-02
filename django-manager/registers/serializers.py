from rest_framework.serializers import ModelSerializer

from .models import Product


class ProductSerializer(ModelSerializer):
    """
    Serializer for the Product model
    """
    class Meta:
        model = Product
