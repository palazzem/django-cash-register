from django.conf.urls import url

from .views import POSTemplateView


urlpatterns = [
    url(r'^$', POSTemplateView.as_view()),
]
