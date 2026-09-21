from django.urls import path
from . import views

urlpatterns = [
    path('', views.credential_list_create, name='credential-list-create'),
    path('trash/', views.credential_trash, name='credential-trash'),
    path('<str:pk>/', views.credential_detail, name='credential-detail'),
    path('<str:pk>/restore/', views.credential_restore, name='credential-restore'),
    path('<str:pk>/permanent/', views.credential_permanent_delete, name='credential-permanent-delete'),
]
