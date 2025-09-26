from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from portal.dashboards.plotly_dashboards import dashboard_ventas_cliente, dashboard_ventas_seccion
# Create your views here.

class Homeview(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ventas_seccion'] = dashboard_ventas_seccion()
        context['ventas_cliente'] = dashboard_ventas_cliente()
        return context

class CustomLoginView(LoginView):
    template_name = 'login.html'

class CustomLogoutView(LogoutView):
    next_page = '/login/'

