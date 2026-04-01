from django.urls import path

from . import views

app_name = 'fastpass'

urlpatterns = [
    path('', views.home, name='home'),
    path('zones/', views.zone_list, name='zone_list'),
    path('zones/<int:zone_id>/', views.zone_detail, name='zone_detail'),
    path('attractions/', views.attraction_list, name='attraction_list'),
    path('attractions/<int:pk>/', views.attraction_detail, name='attraction_detail'),
    path('short-waits/', views.short_wait_rides, name='short_waits'),
    path('guest/login/', views.guest_login, name='guest_login'),
    path(
        'guest/<int:guest_id>/dashboard/',
        views.guest_dashboard,
        name='guest_dashboard',
    ),
    path(
        'book/<int:attraction_id>/',
        views.book_fastpass,
        name='book_fastpass',
    ),
]
