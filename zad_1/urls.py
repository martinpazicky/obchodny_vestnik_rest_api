from django.urls import path, re_path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('v1/health/', views.health, name='health'),
    path('v1/ov/submissions/', views.submissions, name='submissions'),
    path('v2/ov/submissions/', views.v2submissions, name='v2submissions'),
    path('v1/ov/submissions/<int:record_id>', views.submissions, name='submissions'),
    path('v2/ov/submissions/<int:record_id>', views.v2submissions, name='v2submissions'),
    path('v1/ov/submissions/<int:record_id>/', views.submissions, name='submissions'),
    path('v2/ov/submissions/<int:record_id>/', views.v2submissions, name='v2submissions'),
    path('v1/companies/', views.companies, name='companies'),
    path('v2/companies/', views.v2companies, name='v2companies')
]