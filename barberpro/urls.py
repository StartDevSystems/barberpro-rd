"""
URL configuration for barberpro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include
from scheduling import views as scheduling_views

urlpatterns = [
    path('', scheduling_views.PublicServiceListView.as_view(), name='public_home'),
    path('book/service/<int:service_id>/', scheduling_views.BookingView.as_view(), name='public_booking'),
    path('booking/confirmation/<int:pk>/', scheduling_views.BookingConfirmationView.as_view(), name='public_booking_confirmation'),
    
    # URL para la API de disponibilidad
    path('api/available-slots/', scheduling_views.get_available_slots, name='api_available_slots'),

    # Rutas del panel de admin interno
    path('admin/', admin.site.urls),
    path('app/', include('scheduling.urls', namespace='scheduling')),
]
