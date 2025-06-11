from django.urls import path
from .views import filter_journals, register, change_password, get_profile, update_user, reset_password_request, reset_password_confirm,journal_list, journal_create, journal_detail,journal_update, journal_delete
from . import views
urlpatterns = [
    path('journals/filter/', filter_journals),
    path('register/', register, name='register'),
    path('journals/', journal_list),
    path('change-password/', change_password, name='change-password'),
    path('me/', get_profile, name='get-profile'),
    path('update-user/', update_user, name='update-user'),
    path('reset-password/', reset_password_request, name='reset-password'),
    path('reset-password-confirm/<uidb64>/<token>/', reset_password_confirm, name='reset-password-confirm'),
    path('journals/', views.journal_list_create, name='journal-list-create'),
    path('journals/<int:pk>/', views.journal_detail, name='journal-detail'),
    path('journals/', journal_list, name='journal-list'),
    path('journals/create/', journal_create, name='journal-create'),
    path('journals/<int:pk>/', journal_detail, name='journal-detail'),
    path('journals/<int:pk>/update/', journal_update, name='journal-update'),
    path('journals/<int:pk>/delete/', journal_delete, name='journal-delete'),
]

