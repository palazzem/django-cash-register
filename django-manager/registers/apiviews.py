from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAdminUser

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    The ``ProductViewSet`` API, provides only the list of the configured
    products, and doesn't allow any [C-UD] interaction.
    """
    permission_classes = (IsAdminUser,)

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
