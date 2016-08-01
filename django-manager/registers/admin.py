from django.contrib import admin

from .models import Product, Recipe, Sell


class SellInline(admin.TabularInline):
    model = Sell
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        SellInline,
    ]


admin.site.register(Product)
