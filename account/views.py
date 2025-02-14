from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.views import LoginView


# Create your views here.


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        # user_profile = UserProfileForm(request.POST)
        if form.is_valid():
        # and user_profile.is_valid():
            # profile = user_profile.save(commit=False)
            # profile.user = request.user
            # profile.save()
            form.save()
            messages.success(request, 'Form submitted successfully!')
            return redirect('login')
        else:
            print(form.errors)
            # print(user_profile.errors)
            messages.error(request, 'There was an error. Please fix the highlighted fields.')
    else:
        form = RegisterForm()
        # user_profile = UserProfileForm()

    return render(request, 'registration/register.html', {'form' : form})


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)

def logout_view(request):
    logout(request)
    return redirect('home')