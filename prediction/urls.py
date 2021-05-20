from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('home/',views.home,name='home'),
    path('',views.home,name='home'),
    path('signup',views.signup,name='signup'),
    path('contactus/',views.contactus,name='contactus'),
    path('logout/',auth_views.LogoutView.as_view(),name='logout'),
    path('predict/', views.predict,name='predict'),
    path('crash/',views.crash,name='crash'),
    path('health/',views.health,name='health'),
    path('urban/',views.urban,name='urban'),
    path('population/',views.population,name='population'),
    path('wifi/', views.wifi, name='wifi'),
    path('parking/', views.parking,name='parking'),
    path('aboutus/', views.aboutus,name='aboutus'),
    path('parkingdashboard/', views.parkingdashboard,name='parkingdashboard'),
    path('parkinganalysis/', views.parkinganalysis,name='parkinganalysis'),
    path('form/', views.weather_form, name = 'weatherform'),
    path('region/', views.region_form, name = 'wc'),
    path('prediction/', views.weather_prediction, name = 'wp'),
    path('AQI/', views.AQI, name = 'AQI'),
    path('AQI_form/', views.AQI_form, name = 'AQI_form')
]