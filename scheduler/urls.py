from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('funcionarios/', views.employee_list, name='employee_list'),
    path('funcionarios/novo/', views.employee_create, name='employee_create'),
    path('funcionarios/<int:user_id>/editar/', views.employee_update, name='employee_update'),
    path('funcionarios/<int:user_id>/excluir/', views.employee_delete, name='employee_delete'),
    path('reunioes/', views.meeting_list, name='meeting_list'),
    path('reunioes/nova/', views.meeting_create, name='meeting_create'),
    path('reunioes/<int:meeting_id>/', views.meeting_detail, name='meeting_detail'),
    path('reunioes/<int:meeting_id>/editar/', views.meeting_update, name='meeting_update'),
    path('reunioes/<int:meeting_id>/excluir/', views.meeting_delete, name='meeting_delete'),
    path('convites/', views.invitation_list, name='invitation_list'),
    path('convites/<int:invitation_id>/', views.invitation_detail, name='invitation_detail'),
]
