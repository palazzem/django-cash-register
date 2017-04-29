"""
These tests don't check the validity of the ViewSet or of the
Serializer but only assert that the ``python-cash-register``
integration works properly.
"""
import pytest

from model_mommy import mommy

from django.core.urlresolvers import reverse

from serial import SerialException

from registers import adapters
from registers.models import Product, Receipt
from registers.receipts import convert_serializer
from registers.serializers import ReceiptSerializer


@pytest.mark.django_db
def test_receipt_post_print(alice_client, mocker, settings):
    """
    Ensure that a POST on the receipt endpoint prints a receipt
    through the connected cash register.
        * create two products
        * prepare a payload with 2 sold items
        * POST the message
        * expect that the receipt is printed
    """
    # force the print
    settings.REGISTER_PRINT = True
    # spy third party libraries and mock the serial port
    mocker.patch('registers.adapters.printers.Serial')
    sell_products = mocker.spy(adapters.printers.SaremaX1, 'sell_products')
    send = mocker.spy(adapters.printers.SaremaX1, 'send')
    # create some products
    products = mommy.make(Product, _quantity=2)
    # sold products
    sold_items = {
        'products': [
            {
                'id': products[0].id,
                'price': '5.90',
            },
            {
                'id': products[1].id,
                'price': '2.00',
                'quantity': '2.0',
            },
        ]
    }
    # get the receipts endpoint
    endpoint = reverse('registers:receipt-list')
    response = alice_client.post(endpoint, data=sold_items)
    # the receipt has been created through the ``ReceiptSerializer``
    assert response.status_code == 201
    assert sell_products.call_count == 1
    assert send.call_count == 1


@pytest.mark.django_db
def test_receipt_post_without_print(alice_client, mocker):
    """
    Ensure that a POST on the receipt endpoint doesn't print a receipt
    if an internal Django settings is set to stop this action.
        * create two products
        * prepare a payload with 2 sold items
        * POST the message
        * expect that the receipt is not printed
    """
    # mock third party libraries
    sell_products = mocker.spy(adapters.printers.SaremaX1, 'sell_products')
    send = mocker.spy(adapters.printers.SaremaX1, 'send')
    # create some products
    products = mommy.make(Product, _quantity=2)
    # sold products
    sold_items = {
        'products': [
            {
                'id': products[0].id,
                'price': '5.90',
            },
            {
                'id': products[1].id,
                'price': '2.00',
                'quantity': '2.0',
            },
        ]
    }
    # get the receipts endpoint
    endpoint = reverse('registers:receipt-list')
    response = alice_client.post(endpoint, data=sold_items)
    # the receipt has been created through the ``ReceiptSerializer``
    # without printing the receipt
    assert response.status_code == 201
    assert sell_products.call_count == 0
    assert send.call_count == 0


@pytest.mark.django_db
def test_receipt_post_rollback_on_print_errors(alice_client, mocker, settings):
    """
    Ensure that a POST on the receipt endpoint prints a receipt
    through the connected cash register. This test doesn't check
    the validity of the ViewSet / Serializer but only assert
    that the python-cash-register integration works properly.
        * create two products
        * prepare a payload with 2 sold items
        * POST the message
        * expect that an exception is raised and that the database
          did a rollback
    """
    # force the print
    settings.REGISTER_PRINT = True
    # simulate a serial exception
    mock_serial = mocker.patch('registers.adapters.printers.Serial')
    mock_serial.side_effect = SerialException
    # create some products
    products = mommy.make(Product, _quantity=3)
    # sold products
    sold_items = {
        'products': [
            {
                'id': products[0].id,
                'price': '5.90',
            },
            {
                'id': products[1].id,
                'price': '2.00',
                'quantity': '2.0',
            },
            {
                'id': products[2].id,
                'price': '1.00',
                'quantity': '1.68',
            },
        ]
    }
    # get the receipts endpoint
    endpoint = reverse('registers:receipt-list')
    response = alice_client.post(endpoint, data=sold_items)
    # an exception is raised and it causes a 500 error
    error = 'The connected cash register is not ready. Please check the connection'
    assert response.status_code == 500
    assert response.data['detail'] == error
    # no receipts must be created
    assert Receipt.objects.count() == 0


@pytest.mark.django_db
def test_convert_serializer():
    """
    Test the ``convert_serializer`` method so that for the given
    ``ReceiptSerializer`` it returns a list of sold items that must
    be printed.
    """
    # create a list of products
    products = mommy.make(Product, _quantity=3)
    # products that are sold
    receipt = {
        'products': [
            {
                'id': products[0].id,
                'price': '5.90',
            },
            {
                'id': products[1].id,
                'price': '2.00',
                'quantity': '2',
            },
            {
                'id': products[2].id,
                'price': '1.00',
                'quantity': '1',
            },
        ]
    }
    # create a valid serializer
    serializer = ReceiptSerializer(data=receipt)
    serializer.is_valid()
    # convert the serializer
    expected = [
        {
            'description': products[0].name,
            'price': '5.90',
        },
        {
            'description': products[1].name,
            'price': '2.00',
            'quantity': '2.00',
        },
        {
            'description': products[2].name,
            'price': '1.00',
        },
    ]
    assert convert_serializer(serializer) == expected
