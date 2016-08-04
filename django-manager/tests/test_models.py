import pytest

from django.utils import timezone

from model_mommy import mommy

from registers.models import Product, Receipt


class TestProduct:
    @pytest.mark.django_db
    def test_default_attributes(self):
        """
        Test that the ``Product`` model has the right attributes,
        required to print a receipt.
        """
        # create a product
        product = mommy.make(Product)
        # check default attributes
        assert product.name is not None
        assert product.default_price is not None
        assert product.default_price_currency == 'EUR'
        assert product.icon is not None
        # check representation
        assert str(product) == product.name

    @pytest.mark.django_db
    def test_str(self):
        """
        Test the ``Product`` representation
        """
        # create a product
        product = mommy.make(Product)
        # check representation
        assert str(product) == product.name


class TestReceipt:
    @pytest.mark.django_db
    def test_default_attributes(self):
        """
        Test that the ``Receipt`` model has the right attributes,
        required to print a receipt.
        """
        # create a receipt
        receipt = mommy.make(Receipt)
        # check default attributes
        assert receipt.date is not None
        assert receipt.products.count() == 0

    @pytest.mark.django_db
    def test_auto_now_date(self):
        """
        Test that the ``Receipt`` model has an auto_now_add field
        as a date
        """
        # get the current time
        now = timezone.now()
        # create a receipt
        receipt = mommy.make(Receipt)
        # test the field
        assert now < receipt.date

    @pytest.mark.django_db
    def test_str(self):
        """
        Test the ``Receipt`` representation
        """
        # create a receipt
        receipt = mommy.make(Receipt)
        # update the receipt auto_now_add attribute
        new_time = timezone.datetime(2016, 1, 1)
        receipt.date = new_time
        receipt.save()
        # check default attributes
        assert str(receipt) == 'Total: 0.0 -- Jan. 1, 2016, midnight'

    @pytest.mark.django_db
    def test_receipt_with_sold_items(self):
        """
        Ensures that a ``Receipt`` has a ManyToMany relationship with ``Product``
        model. The ralationship must have required attributes to print
        a valid receipt.
        """
        # create a receipt
        receipt = mommy.make(Receipt, make_m2m=True)
        # check products list
        assert receipt.products.count() == 5
        # ensures that the ManyToMany has the right attributes
        m2m_fields = receipt.products.through.objects.all()[0]
        assert m2m_fields.receipt is not None
        assert m2m_fields.product is not None
        assert m2m_fields.quantity is not None
        assert m2m_fields.price is not None
