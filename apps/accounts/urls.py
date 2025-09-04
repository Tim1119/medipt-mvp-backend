from django.urls import path,include
from .views import OrganizationSignupView

urlpatterns = [
   path('organization-signup/',OrganizationSignupView.as_view(),name='organization-signup'),
]

