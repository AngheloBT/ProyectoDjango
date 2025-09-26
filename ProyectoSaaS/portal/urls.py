from django.urls import path
from .views import CustomLoginView, CustomLogoutView, Homeview


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name= 'login' ),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', Homeview.as_view(), name='app')
]