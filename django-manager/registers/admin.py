from django.contrib import admin

from .models import Product, Receipt, Sell


class SellInline(admin.TabularInline):
    model = Sell
    extra = 1


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    inlines = [
        SellInline,
    ]


admin.site.register(Product)
