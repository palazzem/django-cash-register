"""
These tests don't check the validity of the ViewSet or of the
Serializer but only assert that the ``python-cash-register``
integration works properly.
"""
import pytest

from serial import SerialException

from registers import adapters
from registers.exceptions import AdapterPushFailed
from registers.adapters.printers import CashRegisterAdapter


@pytest.mark.django_db
def test_cash_register_adapter(mocker):
    """
    Ensure that a list of sold items is printed:
        * prepare a payload with 2 sold items
        * push the adapter
        * expect that the receipt is printed
    """
    # initialize the adapter
    adapter = CashRegisterAdapter()
    # spy third party libraries and mock the serial port
    mocker.patch('registers.adapters.printers.Serial')
    sell_products = mocker.spy(adapters.printers.SaremaX1, 'sell_products')
    send = mocker.spy(adapters.printers.SaremaX1, 'send')
    # sold products
    sold_items = [
        {
            'description': 'Croissant',
            'price': '5.90',
        },
        {
            'description': 'Begel',
            'price': '2.00',
            'quantity': '2.00',
        },
    ]
    # push data
    adapter.push(sold_items)
    assert sell_products.call_count == 1
    assert send.call_count == 1


@pytest.mark.django_db
def test_cash_register_adapter_failure(mocker):
    """
    Ensure that an AdapterPushFailed is raised when using this
    adapter:
        * prepare a payload with 2 sold items
        * push the adapter
        * expect that an exception is raised
    """
    # initialize the adapter
    adapter = CashRegisterAdapter()
    # mock the serial port so that it raises an Exception
    serial_port = mocker.patch('registers.adapters.printers.Serial')
    serial_port.side_effect = SerialException
    # sold products
    sold_items = [
        {
            'description': 'Croissant',
            'price': '5.90',
        },
        {
            'description': 'Begel',
            'price': '2.00',
            'quantity': '2.00',
        },
    ]
    # push data and check the Exception
    with pytest.raises(AdapterPushFailed) as excinfo:
        adapter.push(sold_items)
    assert excinfo.typename == 'CashRegisterNotReady'
