from rest_framework.routers import DefaultRouter
from authentication.api.viewsets import BarberShopViewSet

router = DefaultRouter()
router.register(r'salao', BarberShopViewSet)


# As URLs finais serão '/api/v1/salao/' e '/api/v1/salao/{pk}/'
urlpatterns = router.urls
