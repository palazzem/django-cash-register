import pytest

from django.utils import timezone

from model_mommy import mommy

from registers.models import Product, Recipe


class TestProduct:
    @pytest.mark.django_db
    def test_default_attributes(self):
        """
        Test that the ``Product`` model has the right attributes,
        required to print a recipe.
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


class TestRecipe:
    @pytest.mark.django_db
    def test_default_attributes(self):
        """
        Test that the ``Recipe`` model has the right attributes,
        required to print a recipe.
        """
        # create a recipe
        recipe = mommy.make(Recipe)
        # check default attributes
        assert recipe.date is not None
        assert recipe.products.count() == 0


    @pytest.mark.django_db
    def test_auto_now_date(self):
        """
        Test that the ``Recipe`` model has an auto_now_add field
        as a date
        """
        # get the current time
        now = timezone.now()
        # create a recipe
        recipe = mommy.make(Recipe)
        # test the field
        assert now < recipe.date


    @pytest.mark.django_db
    def test_str(self):
        """
        Test the ``Recipe`` representation
        """
        # create a recipe
        recipe = mommy.make(Recipe)
        # update the recipe auto_now_add attribute
        new_time = timezone.datetime(2016, 1, 1)
        recipe.date = new_time
        recipe.save()
        # check default attributes
        assert str(recipe) == 'Total: 0.0 -- Jan. 1, 2016, midnight'


    @pytest.mark.django_db
    def test_recipe_with_sold_items(self):
        """
        Ensures that a ``Recipe`` has a ManyToMany relationship with ``Product``
        model. The ralationship must have required attributes to print
        a valid recipe.
        """
        # create a recipe
        recipe = mommy.make(Recipe, make_m2m=True)
        # check products list
        assert recipe.products.count() == 5
        # ensures that the ManyToMany has the right attributes
        m2m_fields = recipe.products.through.objects.all()[0]
        assert m2m_fields.recipe is not None
        assert m2m_fields.product is not None
        assert m2m_fields.quantity is not None
        assert m2m_fields.price is not None
