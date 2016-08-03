from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from .apiviews import ProductViewSet, RecipeViewSet


app_name = 'registers'
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'recipes', RecipeViewSet)
urlpatterns = router.urls
