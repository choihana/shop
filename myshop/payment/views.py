from _decimal import Decimal

import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from orders.models import Order

# create the Stripe instance
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION
def payment_process(request):
    #order_id session key 가져오기
    order_id = request.session.get('order_id', None)
    # order_id 세션키로 현재 Order 객체를 데이터베이스에서 가져옴
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        success_url = request.build_absolute_uri(
            reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(
            reverse('payment:canceled'))
        #Stripe checkout session data
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id ,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': [] #A list of items the customer is purchasing
        }
        # 주문 항목을 stripe checkout 세션에 추가
        for item in order.items.all():
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item.price * Decimal('100')),
                    'currency':'usd',
                    'product_data':{
                        'name':item.product.name,
                    },
                },

                'quantity': item.quantity,
            })
        # coupon apply
        if order.coupon:
            stripe_coupon = stripe.Coupon.create(
                name= order.coupon.code,
                percent_off = order.discount,
                duration = 'once', # 1회성 사용임
            )
            # 쿠폰을 결제 세션에 연결
            session_data['discounts'] = [{'coupon':stripe_coupon.id}]

        # create stripe checkout session
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code =303)
    return render(request, 'payment/process.html', {'order':order})

def payment_completed(request):
    return render(request, 'payment/completed.html')

def payment_canceled(request):
    return render(request, 'payment/canceled.html')