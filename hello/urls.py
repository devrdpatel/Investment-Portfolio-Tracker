from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name="index"),
    path('transactions/', views.transaction_list, name="transaction_list"),
    path('transactions/add', views.transaction_create, name="transaction_create"),
    path('transactions/edit/<int:id>', views.transaction_edit, name="transaction_edit"),
    path('transactions/delete/<int:id>', views.transaction_delete, name="transaction_delete"),
    path("transactions/report/", views.transaction_report, name="transaction_report"),
]