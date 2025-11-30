from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label = "Correo Electronico",
        widget = forms.TextInput(attrs={'class': 'form-control w-100 rounded-3 bg-light', 'placeholder': '📧 tu@email.cl'}) 
    )
    password = forms.CharField(
        label = "Contraseña",
        widget = forms.PasswordInput(attrs={'class': 'form-control w-100 rounded-3 bg-light', 'placeholder': '🔒 ********'})
    )

class CustomRegisterForm(UserCreationForm):
    tipo_de_usuario=[
        ('empleado', 'Empleado'),
        ('administrador', 'Administrador'),
    ]

    tipo_usuario = forms.ChoiceField(
        choices = [('', 'Selecciona tipo de cuenta')] + tipo_de_usuario,
        widget = forms.Select(attrs={'class': 'form-control w-100'}),
        label = 'Tipo de cuenta'
    )
    class Meta:
        model = CustomUser
        fields = ['username', 'rut', 'first_name', 'last_name','telefono', 'password1', 'password2']
        labels = {
            'username': 'Correo Electronico',
            'rut': 'RUT',
            'first_name' : 'Nombre',
            'last_name': 'Apellido',
            'telefono': 'Teléfono',
            }
        widgets = {
            'username': forms.EmailInput(attrs={'class': 'form-control w-100', 'placeholder': 'Correo Electronico'}),
            'rut': forms.TextInput(attrs={'class': 'form-control w-100', 'placeholder': '12345678-9'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control w-100', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control w-100', 'placeholder': 'Apellido'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control w-100', 'placeholder': '+56912345678'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar Contraseña'
        self.fields['password1'].widget.attrs.update({'class': 'form-control w-100', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control w-100', 'placeholder': 'Confirmar Contraseña'})

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['tipo_usuario'] == 'administrador':
            user.is_superuser = True
            user.is_staff = True
        if commit:
            user.save()
        return user
    
class CustomEditForm(forms.ModelForm):
    tipo_de_usuario=[
        ('empleado', 'Empleado'),
        ('administrador', 'Administrador'),
    ]

    tipo_usuario = forms.ChoiceField(
        choices = [('', 'Selecciona tipo de cuenta')] + tipo_de_usuario,
        widget = forms.Select(attrs={'class': 'form-control w-100'}),
        label = 'Tipo de cuenta'
    )
    class Meta:
        model = CustomUser
        fields = ['username', 'rut', 'first_name', 'last_name','telefono']
        labels = {
            'username': 'Correo Electronico',
            'rut': 'RUT',
            'first_name' : 'Nombre',
            'last_name': 'Apellido',
            'telefono': 'Teléfono',
            }
        widgets = {
            'username': forms.EmailInput(attrs={'class': 'form-control w-100', 'placeholder': 'Correo Electronico'}),
            'rut': forms.TextInput(attrs={'class': 'form-control w-100', 'placeholder': '12345678-9'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control w-100', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control w-100', 'placeholder': 'Apellido'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control w-100', 'placeholder': '+56912345678'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['tipo_usuario'] == 'administrador':
            user.is_superuser = True
            user.is_staff = True
        else:
            user.is_superuser = False
            user.is_staff = False
        if commit:
            user.save()
        return user