import pytest

from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image

from rest_framework.test import APIClient


@pytest.fixture
def temp_image():
    """
    Creates an empty in-memory image that is uploaded as
    a Django ``InMemoryUploadedFile``. This fixture can be
    used in DRF serializers when a fake image is required.
    """
    # create an in-memory bytes stream
    memory_fp = BytesIO()
    # create an empty RGB image
    image = Image.new('RGB', (1, 1))
    image.save(memory_fp, format='PNG')
    # use an in-memory uploaded file
    image_file = InMemoryUploadedFile(
        memory_fp,
        field_name='tempfile',
        name='tempfile.png',
        content_type='image/png',
        size=len(memory_fp.getvalue()),
        charset='utf-8',
    )
    # return the image
    image_file.seek(0)
    return image_file


@pytest.fixture
def api_client():
    """
    Returns a Django REST Framework APIClient
    """
    return APIClient()


@pytest.fixture
def alice_client(api_client, django_user_model):
    """
    Alice is a superuser and this is her ``APIClient``
    instance already logged in.
    """
    # Alice is an admin user
    django_user_model.objects.create_superuser(
        username='alice',
        email='alice@shop.com',
        password='123456',
    )
    api_client.login(username='alice', password='123456')
    return api_client


@pytest.fixture
def bob_client(api_client, django_user_model):
    """
    Bob is a regular user and this is his ``APIClient``
    instance already logged in.
    """
    # Bob is a regular user
    django_user_model.objects.create_user(username='bob', password='123456')
    api_client.login(username='bob', password='123456')
    return api_client
