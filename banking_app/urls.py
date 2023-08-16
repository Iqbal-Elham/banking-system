from django.urls import path
from .views import ContactUsView

app_name = 'banking_app'

urlpatterns = [
    path('contact/', ContactUsView.as_view(), name='contact_us'),
]