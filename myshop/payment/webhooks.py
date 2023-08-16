import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order


@csrf_exempt #csrf 검증 수행하지 않도록하는 데코레이터 (strip과의 약속)
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # invalid payload
        return HttpResponse(status = 400)
    except stripe.error.SignatureVerificationError as e:
        # invalid signature
        return HttpResponse(status = 400)

    # 결제 이벤트 체크
    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                order = Order.objects.get(id=session.client_reference_id)
            except Order.DoesNotExist:
                return HttpResponse(status = 404)
            order.paid = True
            # 결제 완료 시, 결제 인텐트 ID 저장
            order.stripe_id = session.payment_intent
            order.save()

    # success
    return HttpResponse(status =200)
