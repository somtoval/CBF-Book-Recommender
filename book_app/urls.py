# urls.py
from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('recommendations/<int:book_id>/', views.get_recommendations, name='get_recommendations'),
]