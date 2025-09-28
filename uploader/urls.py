# uploader/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_document, name='upload_document'),
    path('success/', views.upload_success, name='upload_success'),
    path('search/', views.search_documents, name='search'),
    # Add this new URL for viewing a single document
    path('document/<int:pk>/', views.document_detail, name='document_detail'),
]