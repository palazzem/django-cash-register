"""
These tests don't check the validity of the ViewSet or of the
Serializer but only assert that the ``python-cash-register``
integration works properly.
"""
import pytest

from model_mommy import mommy

from django.core.urlresolvers import reverse

from registers import apiviews
from registers.models import Product
from registers.receipts import convert_serializer
from registers.serializers import RecipeSerializer


@pytest.mark.django_db
def test_receipt_post_print(api_client, django_user_model, mocker, settings):
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
    mocker.patch('registers.receipts.Serial')
    convert_serializer = mocker.spy(apiviews, 'convert_serializer')
    print_receipt = mocker.spy(apiviews, 'print_receipt')
    # create some products
    products = mommy.make(Product, _quantity=2)
    # Alice is an admin user
    alice = django_user_model.objects.create_superuser(
        username='alice',
        email='alice@shop.com',
        password='123456',
    )
    api_client.login(username='alice', password='123456')
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
    endpoint = reverse('registers:recipe-list')
    response = api_client.post(endpoint, data=sold_items)
    # the recipe has been created through the ``RecipeSerializer``
    assert response.status_code == 201
    assert convert_serializer.call_count == 1
    assert print_receipt.call_count == 1


@pytest.mark.django_db
def test_receipt_post_without_print(api_client, django_user_model, mocker):
    """
    Ensure that a POST on the receipt endpoint doesn't print a receipt
    if an internal Django settings is set to stop this action.
        * create two products
        * prepare a payload with 2 sold items
        * POST the message
        * expect that the receipt is not printed
    """
    # mock third party libraries
    convert_serializer = mocker.patch('registers.apiviews.convert_serializer')
    print_receipt = mocker.patch('registers.apiviews.print_receipt')
    # create some products
    products = mommy.make(Product, _quantity=2)
    # Alice is an admin user
    alice = django_user_model.objects.create_superuser(
        username='alice',
        email='alice@shop.com',
        password='123456',
    )
    api_client.login(username='alice', password='123456')
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
    endpoint = reverse('registers:recipe-list')
    response = api_client.post(endpoint, data=sold_items)
    # the recipe has been created through the ``RecipeSerializer``
    assert response.status_code == 201
    assert convert_serializer.call_count == 0
    assert print_receipt.call_count == 0


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
    recipe = {
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
    serializer = RecipeSerializer(data=recipe)
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
