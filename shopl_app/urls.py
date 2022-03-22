from shopl_app import views
from django.urls import path

urlpatterns = [
    path('get',views.get_hello)
]
