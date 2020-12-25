from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import get_user_model, views
from django.core.cache import cache
from django import forms

User = get_user_model()


def receive_user_uuid(request, user_uuid, *args, **kwargs):
    if user_uuid:
        try:
            user = cache.get(user_uuid)
            if user:
                if user.is_active:
                    return HttpResponse('No Need to verify. Done before')
                else:
                    return redirect('set-pass', user_uuid=user_uuid)
            else:
                return HttpResponse('BAD verification key')

        except Exception as e:
            print(e)
            return HttpResponse('Unhandled Error')


def validate_password(value):
    if len(value) < 8:
        raise ValidationError(
            _('%(value) is too small'),
            params={'value': value},
        )


class SetPass(forms.Form):
    username = forms.CharField(required=False, help_text='optional')
    password = forms.CharField(
        widget=forms.PasswordInput, validators=[validate_password])


class SetEmail(forms.Form):
    email = forms.EmailField()


class Login(views.LoginView):
    template_name = 'login.html'
    LOGIN_REDIRECT_URL = 'home'


class Logout(views.LogoutView):
    template_name = 'login.html'
    next_page = 'home'


def home(request):
    if request.user.is_authenticated:
        return HttpResponse(f'{request.user} is {"active" if request.user.is_active else "not active"}')
    else:
        return HttpResponse('Who are you ?')


def signup(requset):
    if requset.method == 'GET':
        form = SetEmail()
        return render(requset, 'login.html', context={'form': form})
    if requset.method == 'POST':
        form = SetEmail(requset.POST)
        if form.is_valid():
            email = requset.POST.get('email')
            user_created = User.objects.get_or_create(
                email=email, username=email)
            if user_created == True:
                return HttpResponse('go to your inbox')
            else:
                return redirect('login')


def set_pass(request, user_uuid, *args, **kwargs):
    if request.method == 'GET':
        form = SetPass()
        return render(request, 'login.html', context={'form': form})
    if request.method == 'POST':
        form = SetPass(request.POST)
        if form.is_valid():
            user = cache.get(user_uuid)
            password = request.POST.get('password', None)
            username = request.POST.get('username', None)
            if username:
                user.username = username
            if password:
                user.set_password(password)
                user.is_active = True
                user.save()
                cache.delete(user_uuid)
                return redirect('login')
            return HttpResponse('Failed')
        return redirect('set-pass', user_uuid=user_uuid)
