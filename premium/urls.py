from django.urls import path
from . import views

app_name = 'premium'
urlpatterns = [
    path('', views.premium_form, name='premium_form'),
    path('plans/', views.premium_plans, name='premium_plans'),
    path('payment-methods/', views.payment_methods, name='payment_methods'),
    path('dashboard/', views.premium_dashboard, name='premium_dashboard'),
    path('analytics/', views.premium_analytics, name='premium_analytics'),
    path('checkout/<str:plan_type>/<int:property_pk>/', views.premium_checkout, name='premium_checkout'),
    path('qr-payment/<str:plan_type>/<int:property_pk>/', views.qr_payment, name='qr_payment'),
    path('processing/<str:plan_type>/<int:property_pk>/<str:payment_method>/', views.payment_processing, name='payment_processing'),
    path('badge/', views.premium_badge, name='premium_badge'),
    path('create/<int:property_pk>/', views.premium_create, name='premium_create'),
    path('<int:pk>/update/', views.premium_update, name='premium_update'),
    path('<int:pk>/delete/', views.premium_delete, name='premium_delete'),
]
