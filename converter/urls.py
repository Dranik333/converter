from django.urls import path
from . import views 

urlpatterns = [
    path('converter/', views.currency_converter, name='currency_converter'),
    path('', views.index, name='index' ),
    path('about/', views.about, name='about')
]


