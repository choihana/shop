from django.conf import settings


class Cart:
    def __init__(self, request):
        """
        장바구니 초기화 합니다.
        """

        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    def add(self,product, quantity = 1 , override_quantity = False):
        """
        제품을 장바구니에 추가하거나 수량을 업데이트
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity':0,
                                     'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity

        else:
            self.cart[product_id]['quantity'] += quantity

    def save(self):
        # 세션이 '수정됨'으로 표시되도록 설정하여 저장되도록
        self.session.modified = True