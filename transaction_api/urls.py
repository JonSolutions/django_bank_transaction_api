from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from transaction_api.viewsets import CustomerViewset, TransactionViewset, AccountViewset
from .swagger import schema_view
from .viewsets import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'customers', CustomerViewset, basename='customer')
router.register(r'accounts', AccountViewset, basename='account')
router.register(r'transactions', TransactionViewset, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


