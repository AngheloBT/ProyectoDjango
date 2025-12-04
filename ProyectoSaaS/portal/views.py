from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomRegisterForm, CustomLoginForm, CustomEditForm
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from portal.dashboards.plotly_dashboards import *
from portal.loaders.queries import *
from portal.utils.filters import obtener_filtros
from .models import CustomUser, Section
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
# Create your views here.

class Homeview(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ✅ Obtener filtros desde utils/filters.py
        filtros = obtener_filtros(self.request)

        filtros_aplicar = None if not filtros.get('hay_filtros') else filtros

        # 🔹 Cards principales
        context['cards'] = get_dashboard_cards()
        context['top_products'] = get_top_products(filtros)
        context['clientes_frecuentes'] = get_clientes_frecuentes(filtros)
        context['ventas_recientes'] = get_ventas_recientes(limit=10)

        # 🔹 Dashboards actualizados
        context['ventas_categoria'] = dashboard_ventas_categoria(filtros)
        context['ventas_mensuales'] = dashboard_ventas_mensuales(filtros_aplicar)
        context['lift_asociacion'] = dashboard_lift_asociacion(filtros)
        context['confianza_categoria'] = dashboard_confianza_categoria(filtros)

        # 🔹 Para el selector de categoría
        context['secciones'] = Section.objects.all()
        context['filtros']= filtros
        

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