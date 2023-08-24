from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView


# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'aacount/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('shop:product_list')

class profileView(DetailView):
    template_name = 'shop/product/list.html'
