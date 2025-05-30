from django.urls import path, include
from rest_framework.routers import DefaultRouter
from transaction_api.viewsets import CustomerViewset, TransactionViewset, AccountViewset
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
]


