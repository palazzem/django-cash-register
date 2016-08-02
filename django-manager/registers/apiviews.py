from rest_framework import mixins
from rest_framework import viewsets

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    The ``ProductViewSet`` API, provides only the list of the configured
    products, and doesn't allow any [C-UD] interaction.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
