from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomRegisterForm, CustomLoginForm, CustomEditForm
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from portal.dashboards.plotly_dashboards import dashboard_ventas_seccion, dashboard_lift_confianza, dashboard_ventas_mensuales
from .models import CustomUser
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
# Create your views here.

class Homeview(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ventas_seccion'] = dashboard_ventas_seccion()
        context['ventas_mensuales'] = dashboard_ventas_mensuales()
        context['lift_confianza'] = dashboard_lift_confianza()
        return context

class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomLoginForm

class CustomLogoutView(LogoutView):
    next_page = '/login/'
    
class RegisterView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = CustomUser
    form_class = CustomRegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('list_users')

    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

class ListUsersView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'list_users.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    
class UpdateUserView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CustomUser
    form_class = CustomEditForm
    template_name = 'update_user.html'
    success_url = reverse_lazy('list_users')

    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    
class DeleteUser(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CustomUser
    template_name = 'delete_user.html'
    success_url = reverse_lazy('list_users')

    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return HttpResponseForbidden("No tienes permiso para acceder a esta pagina")

class PasswordRecovery(TemplateView):
    template_name = 'password_recovery.html'