from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm, CustomUserAuthenticationForm
from django.contrib.auth.views import LoginView
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

# Create your views here.


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            login(request, user) 
            return redirect('parts:home')
            
    else:
        form = CustomUserCreationForm()
        
    return render(request, "auth/register.html", {"form": form})

class Login(LoginView):
    template_name = "auth/login.html"
    authentication_form = CustomUserAuthenticationForm
    redirect_authenticated_user = True  # if user is already logged in, redirect

    def get_success_url(self):
        return "/"  
    
    
def user_logout(request):
    logout(request)
    return redirect("accounts:login")


class CurrentUser(DetailView, LoginRequiredMixin):
    model = get_user_model()
    template_name = 'profile.html'
    context_object_name = "user"

    
    def get_object(self, queryset=None):
        """
        Overrides get_object to return the current logged-in user.
        """
        return self.request.user