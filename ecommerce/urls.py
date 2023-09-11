"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import SimpleRouter
from products import views as prod_views
from cart.views import PurchaseViewset

products_router = SimpleRouter()
products_router.register(r'product',prod_views.ProductViewset)

purchase_router = SimpleRouter()
purchase_router.register(r'purchase',PurchaseViewset)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include("authentication.urls")),
    path("category/",prod_views.CategoryListView.as_view(), name="category-list"),
] + products_router.urls + purchase_router.urls
