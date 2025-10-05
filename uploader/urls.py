# uploader/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('upload/', views.upload_document, name='upload_document'),
    path('search/', views.search_documents, name='search'),
    path('document/<int:pk>/', views.document_detail, name='document_detail'),
    
    # New URLs for categories
    path('categories/', views.category_list, name='category_list'),
    path('category/<str:tag_name>/', views.category_detail, name='category_detail'),
]