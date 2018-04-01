from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index),
    path('chart', views.viewer),
    path('get_chart/', views.get_data),
    path('api/exist-table/<slug:subject_code>', views.exist_table)
]
