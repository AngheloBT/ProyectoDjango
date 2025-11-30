from django.urls import path
from .views import CustomLoginView, CustomLogoutView, Homeview, RegisterView, ListUsersView, UpdateUserView, DeleteUser, PasswordRecovery


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name= 'login' ),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', Homeview.as_view(), name='app'),
    path('register/', RegisterView.as_view(), name='register'),
    path('users/', ListUsersView.as_view(), name='list_users'),
    path('users/<int:pk>/edit/', UpdateUserView.as_view(), name='edit_user'),
    path('users/<int:pk>/delete/', DeleteUser.as_view(), name='delete_user'),
    path('passrecovery/', PasswordRecovery.as_view(), name='pass_recovery')
]