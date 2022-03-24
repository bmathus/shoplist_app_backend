from django.urls import path,include

urlpatterns = [
    path('',include("shopl_app.urls"))
]
