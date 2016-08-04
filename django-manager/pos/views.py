from django.views.generic import TemplateView


class POSTemplateView(TemplateView):
    """
    React static application that shows a list of products
    so that the shop owner can sold items with just
    few taps.
    """
    template_name = 'pos.html'
