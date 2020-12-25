from django.urls import path
from .views import receive_user_uuid, set_pass, signup, Login, Logout, home

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='singnup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('<str:user_uuid>/set_password', set_pass, name='set-pass'),
    path('verificationcode/<str:user_uuid>',
         receive_user_uuid, name='signupby-email'),
]
