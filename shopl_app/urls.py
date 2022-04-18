from shopl_app import views
from django.urls import path

urlpatterns = [
    path('auth-user', views.CustomAuthToken.as_view(), name='auth-user'),
    path('lists',views.lists_endpoint),
    path('list/<int:list_id>',views.list_endpoint),
    path('list/<int:list_id>/product/<int:id>',views.product_endpoint),
    path('list/<int:list_id>/product',views.product_add_endpoint),
    path('list/invite',views.invite_endpoint),
    path('list/<int:list_id>/participants',views.particip_endpoint),
    path('call/<int:user_id>',views.call_room_check),
    path('call',views.create_room),
    path('call/end',views.call_end)
]
