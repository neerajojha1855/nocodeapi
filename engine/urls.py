from django.urls import path
from .views import dynamic_api_gateway_router

urlpatterns = [
    path('<slug:api_slug>/', dynamic_api_gateway_router, name='dyn-api-list'),
    path('<slug:api_slug>/<int:pk>/', dynamic_api_gateway_router, name='dyn-api-detail'),
]