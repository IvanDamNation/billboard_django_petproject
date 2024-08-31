from django.urls import path

from .views import (BBLoginView, BBLogoutView, ChangeUserInfoView, BBPasswordChangeView,
                    index, profile, other_page)

app_name = 'main'
urlpatterns = [
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/login/', BBLoginView.as_view(), name='login'),
    path('accounts/logout/', BBLogoutView.as_view(), name='logout'),
    path('accounts/password/change/', BBPasswordChangeView.as_view(), name='password_change'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),
]
