from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from cart.cart import Cart
from orders.forms import OrderCreateForm
from orders.models import OrderItem
from django.urls import reverse
from orders.tasks import order_created
from orders.models import Order


# Create your views here.

def order_create(request):
    cart = Cart(request)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount= cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price = item['price'],
                                         quantity = item['quantity'])

            cart.clear()

            order_created.delay(order.id)
            request.session['order_id'] = order.id
            # redirect for payment
            return redirect(reverse('payment:process'))
            #return render(request, 'orders/order/created.html', {'order':order})
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html',
                  {'cart':cart, 'form':form})

# 관리사이트에 사용자 정의 뷰 추가
@staff_member_required #페이지 요청하는 사용자의 is_active = True & is_staff = True 인지 확인
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin/orders/order/detail.html',
                  {'order':order})