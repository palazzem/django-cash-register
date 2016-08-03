import pytest

from model_mommy import mommy

from django.core.urlresolvers import reverse

from registers.models import Product, Recipe


@pytest.mark.django_db
def test_product_api_ok(api_client, django_user_model):
    """
    Alice is the shop owner (admin), that uses an applications to
    retrieve registered products.
        * Alice is a valid user
        * Alice is a super user
        * Alice retrieves the products list
        * the products list is returned (200)
    """
    # create some products
    products = mommy.make(Product, _quantity=2)
    # Alice is an admin user
    alice = django_user_model.objects.create_superuser(
        username='alice',
        email='alice@shop.com',
        password='123456',
    )
    api_client.login(username='alice', password='123456')
    # get the products endpoint
    endpoint = reverse('registers:product-list')
    response = api_client.get(endpoint)
    # authorized with two products as a response
    assert response.status_code == 200
    assert response.data[0]['name'] == products[0].name
    assert response.data[1]['name'] == products[1].name


@pytest.mark.django_db
def test_product_api_unauthorized_for_regular_user(api_client, django_user_model):
    """
    Bob is a regular user, that wants to retrieve registered products.
    Unfortunately, the endpoint is available only for admin users and
    because of that, he cannot access the API
        * Bob is an authenticated user
        * Bob is a regular user
        * Bob retrieves the products list
        * the products list is not returned (403)
    """
    # Bob is a regular user
    bob = django_user_model.objects.create_user(username='bob', password='123456')
    api_client.login(username='bob', password='123456')
    # get the products endpoint
    endpoint = reverse('registers:product-list')
    response = api_client.get(endpoint)
    # authorized
    assert response.status_code == 403


def test_product_api_unauthorized_for_anonymous(api_client):
    """
    Eve is a malicious user, that uses a custom client to
    retrieve Alice's registered products. Because Eve is not
    a valid user, she must receive a 403
        * Eve is not a registered user
        * Eve retrieves the products list
        * the products list is not returned (403)
    """
    # get the products endpoint
    endpoint = reverse('registers:product-list')
    response = api_client.get(endpoint)
    # unauthorized
    assert response.status_code == 403


@pytest.mark.django_db
def test_recipe_api_ok(api_client, django_user_model):
    """
    Alice is the shop owner (admin), that uses an applications to
    create a new recipe.
        * Alice is a valid user
        * Alice is a super user
        * Alice applicastions posts a list of products to create
          a new recipe
        * the recipe and the products are sold correctly
    """
    # create some products
    products = mommy.make(Product, _quantity=3)
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
            {
                'id': products[2].id,
                'price': '1.00',
                'quantity': '1.68',
            },
        ]
    }
    # get the receipts endpoint
    endpoint = reverse('registers:recipe-list')
    response = api_client.post(endpoint, data=sold_items)
    # the recipe has been created through the ``RecipeSerializer``
    assert response.status_code == 201
    assert Recipe.objects.count() == 1
