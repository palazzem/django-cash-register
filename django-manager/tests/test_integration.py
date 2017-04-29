"""
These tests don't check the validity of the ViewSet or of the
Serializer but only assert that the ``python-cash-register``
integration works properly.
"""
import pytest

from model_mommy import mommy

from django.core.urlresolvers import reverse

from registers.models import Product, Receipt
from registers.receipts import convert_serializer
from registers.exceptions import CashRegisterNotReady
from registers.serializers import ReceiptSerializer


@pytest.mark.django_db
def test_endpoint_calls_adapters(alice_client, mocker, settings):
    """
    Ensure that a POST on the receipt endpoint calls all registered
    adapters:
        * create two products
        * prepare a payload with 2 sold items
        * POST the message
        * expect that the Adapter.push() is executed
    """
    # prepare mock adapters
    adapter_1 = mocker.Mock()
    adapter_2 = mocker.Mock()
    settings.PUSH_ADAPTERS = [adapter_1, adapter_2]
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
    assert adapter_1.push.call_count == 1
    assert adapter_2.push.call_count == 1
    # check the given payload
    args, _ = adapter_1.push.call_args_list[0]
    items = args[0]
    assert items[0]['description'] == products[0].name
    assert items[1]['description'] == products[1].name
    assert items[0]['price'] == '5.90'
    assert items[1]['price'] == '2.00'


@pytest.mark.django_db
def test_receipt_post_rollback_on_adapters_errors(alice_client, mocker, settings):
    """
    Ensure that a POST on the receipt endpoint executes a rollback
    if an internal error happens during adapters execution.
        * create two products
        * prepare a payload with 2 sold items
        * POST the message
        * expect that an exception is raised and that the database
          did a rollback
    """
    # prepare mock adapters
    adapter_1 = mocker.Mock()
    adapter_2 = mocker.Mock()
    settings.PUSH_ADAPTERS = [adapter_1, adapter_2]
    # simulate an exception
    adapter_2.push.side_effect = CashRegisterNotReady
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
    be sent to the push adapters.
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
