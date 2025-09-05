from django.urls import path,include
from .views import LoginAccountView, OrganizationSignupView, ResendActivationLinkView, VerifyAccount

urlpatterns = [
   path('organization-signup/',OrganizationSignupView.as_view(),name='organization-signup'),
   path('verify-account/<str:uidb64>/<str:token>/', VerifyAccount.as_view(), name='verify-account'),
   path('resend-activation-link/',ResendActivationLinkView.as_view(),name='resend-activation-link'),
   path('login/',LoginAccountView.as_view(),name='login-account'),
]

