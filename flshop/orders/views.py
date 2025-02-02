from django.shortcuts import render, redirect
from ..products.models import Product
from django.contrib.auth.decorators import login_required
from forms import OrderForm

def cart_view(request):
    cart = request.session.get('cart', {})
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    cart_items = []
    total = 0
    for product in products:
        quantity = cart[str(product.id)]
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total': product.price * quantity
        })
        total += product.price * quantity
    return render(request, 'orders/cart.html', {'cart_items': cart_items, 'total': total})

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    cart[product_id_str] = cart.get(product_id_str, 0) + 1
    request.session['cart'] = cart
    return redirect('product_list')

# @login_required
# def create_order(request):
#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             # Сохранение заказа и отправка в Telegram
#             ...
#             return redirect('order_success')
#     else:
#         form = OrderForm()
#     return render(request, 'orders/create_order.html', {'form': form})


@login_required
def create_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart_view')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Создаем заказ
            order = form.save(commit=False)
            order.user = request.user

            # Рассчитываем общую стоимость
            total_price = 0
            product_ids = cart.keys()
            products = Product.objects.filter(id__in=product_ids)

            for product in products:
                quantity = cart[str(product.id)]
                total_price += product.price * quantity

            order.total_price = total_price
            order.save()

            # Создаем элементы заказа
            for product in products:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=cart[str(product.id)]
                )

            # Очищаем корзину
            del request.session['cart']

            return redirect('order_success')
    else:
        form = OrderForm()

    return render(request, 'orders/create_order.html', {
        'form': form,
        'cart': cart
    })