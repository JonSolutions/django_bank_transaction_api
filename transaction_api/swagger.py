from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="🔥 De CodeCaptain API",
      default_version='v1',
      description="Django Transaction Api for my swing frontend",
      terms_of_service="https://yourcompany.com/terms/",
      contact=openapi.Contact(email="josef@codecaptain.dev"),
      license=openapi.License(name="MIT"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


token_param = openapi.Parameter(
    'Authorization', openapi.IN_HEADER,
    description="JWT token in format: Bearer <token>",
    type=openapi.TYPE_STRING
)
