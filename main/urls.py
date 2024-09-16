from tkinter.font import names

from django.urls import path

from .views import (BBLoginView, BBLogoutView, ChangeUserInfoView, BBPasswordChangeView,
                    RegisterUserView, RegisterDoneView, DeleteUserView, index, by_rubric,
                    detail, profile, profile_detail, announcement_add, announcement_change,
                    announcement_delete, user_activate, other_page)

app_name = 'main'
urlpatterns = [
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/profile/change/<int:pk>/', announcement_change, name='announcement_change'),
    path('accounts/profile/delete/<int:pk>/', announcement_delete, name='announcement_delete'),
    path('accounts/profile/add/', announcement_add, name='announcement_add'),
    path('accounts/profile/<int:pk>/', profile_detail, name='profile_detail'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/login/', BBLoginView.as_view(), name='login'),
    path('accounts/logout/', BBLogoutView.as_view(), name='logout'),
    path('accounts/password/change/', BBPasswordChangeView.as_view(), name='password_change'),
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('<int:rubric_pk>/<int:pk>/', detail, name='detail'),
    path('<int:pk>/', by_rubric, name='by_rubric'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),
]
