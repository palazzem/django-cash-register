from decimal import Decimal as D

from serial import Serial

from django.conf import settings

from cash_register.models.xditron import SaremaX1


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
        # doesn't work
        if product['quantity'] > 1:
            quantity = str(product['quantity'].quantize(TWOPLACES))
            row.update({'quantity': quantity})

        items.append(row)
    return items


def print_receipt(data):
    """
    Function that prints the passed arguments using a connected
    cash register. It handles the serial communication, raising
    an exception if something goes wrong.
    """
    # define the serial port
    conn = Serial()
    conn.port = settings.SERIAL_PORT
    conn.baudrate = settings.SERIAL_BAUDRATE
    conn.xonxoff = settings.SERIAL_XONXOFF
    conn.timeout = settings.SERIAL_TIMEOUT

    # create a cash register with a serial connection handler
    register = SaremaX1(settings.REGISTER_NAME, connection=conn)

    # prepare and send cash register commands
    register.sell_products(data)
    register.send()
