from django.urls import path
from . import views
from django.urls import include

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_note, name='add_note'),
    path('edit/<int:pk>/', views.edit_note, name='edit_note'),
    path('delete/<int:pk>/', views.delete_note, name='delete_note'),
    path('search/', views.search_notes, name='search_notes'),
    path('register/', views.register, name='register'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.public_profile, name='public_profile'),
    path('note/<int:note_id>/pin/', views.toggle_pin, name='toggle_pin'),
    path('today/', views.todays_notes, name='todays_notes'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),


]
