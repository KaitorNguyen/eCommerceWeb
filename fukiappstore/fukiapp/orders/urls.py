from . import views
from rest_framework import routers
from django.urls import path, include

router = routers.DefaultRouter()
router.register('payment-methods', views.PaymentMethodViewSet)
router.register('orders', views.OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]