from rest_framework.routers import DefaultRouter

from .apiviews import ProductViewSet, ReceiptViewSet


app_name = 'registers'
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'receipts', ReceiptViewSet)
urlpatterns = router.urls
