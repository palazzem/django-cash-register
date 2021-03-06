import pytest

from django.utils import timezone

from model_mommy import mommy

from registers.models import Product, Receipt, Sell


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
        assert str(receipt) == 'Total: 0.00 -- Jan. 1, 2016, midnight'

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

    @pytest.mark.django_db
    def test_receipt_totals(self):
        """
        Test the ``Receipt`` totals when multiple products are added.
        """
        # create a receipt
        product_1 = mommy.make(Product)
        product_2 = mommy.make(Product)
        receipt = mommy.make(Receipt)
        # update the receipt auto_now_add attribute
        new_time = timezone.datetime(2016, 1, 1)
        receipt.date = new_time
        receipt.save()
        # add Sell items
        Sell.objects.create(
            receipt=receipt,
            product=product_1,
            quantity=1,
            price=1,
        )
        Sell.objects.create(
            receipt=receipt,
            product=product_2,
            quantity=2,
            price=2,
        )
        # check default attributes
        assert str(receipt) == 'Total: 5.00 -- Jan. 1, 2016, midnight'

    @pytest.mark.django_db
    def test_multiple_receipt_totals(self):
        """
        Test the ``Receipt`` totals when multiple products are added.
        """
        # create a receipt
        product = mommy.make(Product)
        receipt_1 = mommy.make(Receipt)
        receipt_2 = mommy.make(Receipt)
        # update the receipt auto_now_add attribute
        new_time = timezone.datetime(2016, 1, 1)
        receipt_1.date = new_time
        receipt_2.date = new_time
        receipt_1.save()
        receipt_2.save()
        # add Sell items
        Sell.objects.create(
            receipt=receipt_1,
            product=product,
            quantity=1,
            price=1,
        )
        Sell.objects.create(
            receipt=receipt_2,
            product=product,
            quantity=1,
            price=1,
        )
        # check default attributes
        assert str(receipt_1) == 'Total: 1.00 -- Jan. 1, 2016, midnight'
        assert str(receipt_2) == 'Total: 1.00 -- Jan. 1, 2016, midnight'

    @pytest.mark.django_db
    def test_receipt_default_prices(self):
        """
        Ensures that the `Receipt` products uses the `default_price` if
        that value is not set in the `Sell` model.
        """
        # create a receipt
        product = mommy.make(Product, default_price=2.50)
        receipt = mommy.make(Receipt)
        # update the receipt auto_now_add attribute
        new_time = timezone.datetime(2016, 1, 1)
        receipt.date = new_time
        receipt.save()
        # add Sell items
        Sell.objects.create(
            receipt=receipt,
            product=product,
            quantity=1,
            price=0.0,
        )
        # check default attributes
        assert str(receipt) == 'Total: 2.50 -- Jan. 1, 2016, midnight'

    @pytest.mark.django_db
    def test_receipt_prices_override(self):
        """
        Ensures that the `Receipt` products overrides the `default_price`
        if that value is set in the `Sell` model.
        """
        # create a receipt
        product = mommy.make(Product, default_price=2.50)
        receipt = mommy.make(Receipt)
        # update the receipt auto_now_add attribute
        new_time = timezone.datetime(2016, 1, 1)
        receipt.date = new_time
        receipt.save()
        # add Sell items
        Sell.objects.create(
            receipt=receipt,
            product=product,
            quantity=1,
            price=1.0,
        )
        # check default attributes
        assert str(receipt) == 'Total: 1.00 -- Jan. 1, 2016, midnight'
