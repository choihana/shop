from decimal import Decimal
from django.conf import settings
from shop.models import Product


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

        # 장바구니에 해당 상품이 없다면, 추가해주기 (qunatity = 0 으로 초기화)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity':0,
                                     'price': str(product.price)}
        # override
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity

        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # 세션이 '수정됨'으로 표시되도록 설정하여 저장되도록
        self.session.modified = True

    def remove(self, product):
        """
        장바구니에서 제품을 제거합니다.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        # 장바구니에 있는 항목 id 리스트
        product_ids = self.cart.keys()
        # 장바구니에 있는 항목을 Product 에서 가져오기
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item



    def __len__(self):
        """
        장바구니에 있는 모든 항목을 세어 반환
        :return:
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        #세션에서 장바구니 제거
        del self.session[settings.CART_SESSION_ID]
        self.save()

