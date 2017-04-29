from django.db import transaction
from django.conf import settings

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAdminUser

from .models import Product, Receipt
from .receipts import convert_serializer
from .serializers import ProductSerializer, ReceiptSerializer


class ProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    The ``ProductViewSet`` API, provides only the list of the configured
    products, and doesn't allow any [C-UD] interaction.
    """
    permission_classes = (IsAdminUser,)

    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ReceiptViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    The ``ReceiptViewSet`` API provides an endpoint to create a new ``Receipt``
    according to given products. Indeed the API is not related to a
    particular model but only makes use of a custom ``ReceiptSerializer``
    to store the new ``Receipt`` while printing a new receipt using a
    connected device.
    """
    permission_classes = (IsAdminUser,)

    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer

    def perform_create(self, serializer):
        """
        Save the serializer so that the ``Receipt`` and connected models
        are created, and call all registered ``Adapters``. If one of these
        ``Adapters` fails, a rollback is executed; while this is true for
        many adapters, in general it's not possible to grant consistency because
        ``Adapters` may not have a possible rollback system, and even if
        it's available it may fail again.
        """
        with transaction.atomic():
            # create the ``Receipt`` model, honoring the ManyToMany
            serializer.save()

            # push items list to external components
            items = convert_serializer(serializer)
            for adapter in settings.PUSH_ADAPTERS:
                # TODO: when an adapter is executed, we may store the
                # execution so that it is not executed twice
                adapter.push(items)
