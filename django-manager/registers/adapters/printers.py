from django.conf import settings

from serial import Serial, SerialException
from cash_register.models.xditron import SaremaX1

from .base import BaseAdapter
from ..exceptions import CashRegisterNotReady


class CashRegisterAdapter(BaseAdapter):
    """
    CashRegisterAdapter uses the `python-cash-register` module
    to push data to a real cash register. This is useful if you want
    to use a web UI (or the Django Admin) to create your receipt.

    Data are still persisted in the database so that backfilling
    can be done.
    """
    def push(self, items):
        """
        Function that prints the passed arguments using a connected
        cash register. It handles the serial communication, raising
        an exception if something goes wrong.
        """
        try:
            # define the serial port
            conn = Serial()
            conn.port = settings.SERIAL_PORT
            conn.baudrate = settings.SERIAL_BAUDRATE
            conn.xonxoff = settings.SERIAL_XONXOFF
            conn.timeout = settings.SERIAL_TIMEOUT

            # create a cash register with a serial connection handler
            register = SaremaX1(settings.REGISTER_NAME, connection=conn)

            # prepare and send cash register commands
            register.sell_products(items)
            register.send()
        except SerialException:
            raise CashRegisterNotReady
