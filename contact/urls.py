from django.urls import path
from . import views

app_name = 'contact'
urlpatterns = [
    path('form/', views.contact_form, name='contact_form'),
]
