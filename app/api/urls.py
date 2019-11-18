from rest_framework import routers
from api.views import NumberPlateViewSet

router = routers.SimpleRouter()
router.register(r'plates', NumberPlateViewSet)

urlpatterns = [
]

urlpatterns += router.urls
