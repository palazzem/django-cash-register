from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from .apiviews import ProductViewSet


app_name = 'registers'
router = DefaultRouter()
router.register(r'products', ProductViewSet)
urlpatterns = router.urls
