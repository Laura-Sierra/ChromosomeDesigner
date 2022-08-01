from django.urls import path
from . import views

app_name="public"

urlpatterns = [
    path('', views.index, name='index'),
    path('results', views.results, name='results'),
    path('results2', views.results2, name='results2'),
    path('help', views.help, name='help'),
]