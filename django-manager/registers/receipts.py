from decimal import Decimal as D


# same as Decimal('0.01')
TWOPLACES = D(10) ** -2


def convert_serializer(serializer):
    """
    Utility function that converts the serializer ``validated_data``
    into the proper list supported by the third-party library
    ``python-cash-register``.
    """
    items = []
    for product in serializer.validated_data['products']:
        # base row attributes
        description = product['id'].name
        price = str(product['price'].quantize(TWOPLACES))
        row = {
            'description': description,
            'price': price,
        }

        # append the quantity only if > 1.0
        # Note: the current implementation expects that the shop
        # sells items in unit price instead of other measurement
        # units. Because of that, selling 0.50 kg of stuff
        # is not possible.
        if product['quantity'] > 1:
            quantity = str(product['quantity'].quantize(TWOPLACES))
            row.update({'quantity': quantity})

        items.append(row)
    return items
