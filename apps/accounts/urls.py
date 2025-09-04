from django.urls import path,include
from .views import OrganizationSignupView, VerifyAccount

urlpatterns = [
   path('organization-signup/',OrganizationSignupView.as_view(),name='organization-signup'),
   path('verify-account/<str:uidb64>/<str:token>/', VerifyAccount.as_view(), name='verify-account'),
]

