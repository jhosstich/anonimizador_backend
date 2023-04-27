from django.urls import include, path
from rest_framework import routers
from . import views
from .views import PDFProcessViewSet, TXTProcessViewSetScrubadub

router = routers.DefaultRouter()
router.register(r'heroes', views.HeroViewSet)
#router.register(r'process-pdf', views.PDFProcessViewSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('process-pdf', PDFProcessViewSet.as_view()),
    path('process-txt', TXTProcessViewSetScrubadub.as_view()),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]