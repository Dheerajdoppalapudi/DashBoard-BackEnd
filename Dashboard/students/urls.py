from rest_framework import routers
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', GraduateList.as_view(), name='graduates-list'),
    path('crud/<int:pk>/', GraduateRetriveUpdateDestroy.as_view(), name='graduates-crud'),
    # path('campus/', CampusesList.as_view(), name='campus-list'),
    # path('institute/<str:campus>', InstituteList.as_view(), name='institute-list'),
]