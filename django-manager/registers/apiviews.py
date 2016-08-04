from django.db import transaction
from django.conf import settings

from serial import SerialException

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAdminUser

from .models import Product, Receipt
from .receipts import convert_serializer, print_receipt
from .exceptions import CashRegisterNotReady
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
        are created, but also prints the receipt if the ``REGISTER_PRINT``
        setting is set to ``True``.

        If the variable is set to ``False``, the model is created without printing;
        in a real world example, ``False`` must be used only for development
        mode.
        """
        try:
            with transaction.atomic():
                # create the ``Receipt`` model, honoring the ManyToMany
                serializer.save()

                if settings.REGISTER_PRINT:
                    # convert serializer validated_data and send it
                    # to the cash register printer
                    data = convert_serializer(serializer)
                    print_receipt(data)
        except SerialException:
            raise CashRegisterNotReady
