from django.urls import path

from .views import UserRegistrationView, LogoutView, UserLoginView
from django.contrib.auth import views as auth_views

from .forms import MyResetPassForm, MySetPassForm, MyPasswordChangeForm


app_name = 'accounts'

urlpatterns = [
    path(
        "login/", UserLoginView.as_view(),
        name="user_login"
    ),
    path(
        "logout/", LogoutView.as_view(),
        name="user_logout"
    ),
    path(
        "register/", UserRegistrationView.as_view(),
        name="user_registration"
    ),

    path(
        "password_change/", 
        auth_views.PasswordChangeView.as_view(template_name='accounts/change_password.html',
            form_class=MyPasswordChangeForm,
        ), 
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
        name="password_change_done", 
    ),

    path('password_reset/', auth_views.PasswordResetView.as_view(
        form_class=MyResetPassForm, 
        template_name='registration/password_reset_form.html'), 
        name='password_reset'
        ),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), 
        name='password_reset_done'
        ),

    path('password_reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        form_class=MySetPassForm, 
        template_name='registration/password_reset_confirm.html'), 
        name='password_reset_confirm'
        ),
        
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'),
        name='password_reset_complete'
        ),
]
