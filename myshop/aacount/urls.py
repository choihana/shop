from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import CustomLoginView, profileView

app_name='account'
urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/',LogoutView.as_view(next_page='shop:product_list'), name='logout'),
    path('profile/',profileView.as_view() , name='profile')
]