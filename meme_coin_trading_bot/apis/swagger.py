from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Meme Trading Bot API",
        default_version='v1',
        description="API documentation for Meme Trading Bot",
        contact=openapi.Contact(email="support@memetrading.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)