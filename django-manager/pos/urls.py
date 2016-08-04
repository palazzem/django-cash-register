from django.conf.urls import url, include

from .views import POSTemplateView


urlpatterns = [
    url(r'^$', POSTemplateView.as_view()),
]
