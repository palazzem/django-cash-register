from django.conf import settings
from django.contrib import admin

from .models import Product, Receipt, Sell


def backfill(modeladmin, request, queryset):
    """
    Re-launch the adapters for the given `Receipt`
    queryset.
    """
    for receipt in queryset:
        for adapter in settings.PUSH_ADAPTERS:
            # re-push data
            adapter.push(receipt)
backfill.short_description = 'Backfill data using Adapters'  # noqa


class SellInline(admin.TabularInline):
    model = Sell
    extra = 1


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    actions = [backfill]
    ordering = ['-date']
    inlines = [
        SellInline,
    ]

    def save_related(self, request, form, formsets, change):
        """
        Publish data to registered `Adapters`.
        """
        # save the model as usual
        super().save_related(request, form, formsets, change)
        instance = form.instance
        # push data
        for adapter in settings.PUSH_ADAPTERS:
            adapter.push(instance)


admin.site.register(Product)
