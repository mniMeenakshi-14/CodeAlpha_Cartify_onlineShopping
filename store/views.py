from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.conf import settings
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

import razorpay
import uuid

from .models import Product, Order, OrderItem, Category, Review
from .cart import Cart
from .forms import RegisterForm, CheckoutForm, ReviewForm

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    # --- Search ---
    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # --- Category filter ---
    category_slug = request.GET.get("category", "")
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # --- Price range filter ---
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    context = {
        "products": products,
        "categories": categories,
        "query": query,
        "selected_category": category_slug,
        "min_price": min_price or "",
        "max_price": max_price or "",
    }
    return render(request, "store/product_list.html", context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.select_related("user")

    user_has_reviewed = (
        request.user.is_authenticated
        and reviews.filter(user=request.user).exists()
    )

    review_form = None
    if request.user.is_authenticated and not user_has_reviewed:
        review_form = ReviewForm()

    context = {
        "product": product,
        "reviews": reviews,
        "review_form": review_form,
        "user_has_reviewed": user_has_reviewed,
    }
    return render(request, "store/product_detail.html", context)


@login_required
@require_POST
def submit_review(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.reviews.filter(user=request.user).exists():
        messages.warning(request, "You've already reviewed this product.")
        return redirect("product_detail", pk=pk)

    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        messages.success(request, "Thanks for your review!")
    else:
        messages.error(request, "There was a problem with your review.")

    return redirect("product_detail", pk=pk)


@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = Cart(request)
    quantity = int(request.POST.get("quantity", 1))
    cart.add(product, quantity=quantity)
    messages.success(request, f"Added {product.name} to your cart.")
    return redirect("cart_detail")


@require_POST
def update_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = Cart(request)
    quantity = int(request.POST.get("quantity", 1))
    cart.update(product, quantity=quantity)
    return redirect("cart_detail")


@require_POST
def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = Cart(request)
    cart.remove(product)
    messages.info(request, f"Removed {product.name} from your cart.")
    return redirect("cart_detail")


def cart_detail(request):
    cart = Cart(request)
    return render(request, "store/cart.html", {"cart": cart})


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect("product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create the order as "pending" — it only becomes "paid" once
            # Razorpay confirms payment in payment_verify().
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data["full_name"],
                address=form.cleaned_data["address"],
                status="pending",
            )
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )
                product = item["product"]
                product.stock = max(product.stock - item["quantity"], 0)
                product.save()

            cart.clear()
            return redirect("razorpay_checkout", order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, "store/checkout.html", {"cart": cart, "form": form})


@login_required
def razorpay_checkout(request, order_id):
    """Creates a Razorpay Order and shows the payment page. In
    PAYMENT_MOCK_MODE (the default), no real API call is made — a simulated
    payment page is shown instead, so the whole flow works with zero signup."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    if settings.PAYMENT_MOCK_MODE:
        order.razorpay_order_id = f"mock_order_{uuid.uuid4().hex[:14]}"
        order.save()
        return render(request, "store/mock_checkout.html", {"order": order})

    amount_in_paise = int(order.total_price() * 100)
    razorpay_order = razorpay_client.order.create(
        {
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"order_rcptid_{order.id}",
            "payment_capture": 1,
        }
    )
    order.razorpay_order_id = razorpay_order["id"]
    order.save()

    context = {
        "order": order,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"],
        "amount_in_paise": amount_in_paise,
        "user_email": request.user.email,
    }
    return render(request, "store/razorpay_checkout.html", context)


@login_required
@require_POST
def mock_payment_process(request, order_id):
    """Simulates a Razorpay payment result — no real gateway involved.
    Lets you demo/test both the success and failure paths without any API keys."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    action = request.POST.get("action", "success")

    if action == "success":
        order.status = "paid"
        order.razorpay_payment_id = f"mock_pay_{uuid.uuid4().hex[:14]}"
        order.save()
        messages.success(request, "Payment successful! (simulated — no real gateway used)")
        return redirect("order_success", order_id=order.id)

    return redirect("payment_failed", order_id=order.id)


@csrf_exempt
@login_required
def payment_verify(request, order_id):
    """Called by the JS success handler after the user pays in the Razorpay
    widget. Verifies the payment signature before marking the order paid —
    never trust the client without this check."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    if request.method == "POST":
        params = {
            "razorpay_order_id": request.POST.get("razorpay_order_id"),
            "razorpay_payment_id": request.POST.get("razorpay_payment_id"),
            "razorpay_signature": request.POST.get("razorpay_signature"),
        }
        try:
            razorpay_client.utility.verify_payment_signature(params)
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed. Please try again.")
            return redirect("payment_failed", order_id=order.id)

        order.status = "paid"
        order.razorpay_payment_id = params["razorpay_payment_id"]
        order.save()
        messages.success(request, "Payment successful!")

    return redirect("order_success", order_id=order.id)


@login_required
def payment_failed(request, order_id):
    """User closed the Razorpay widget without paying, or verification
    failed — restore stock and cancel the order."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    if order.status == "pending":
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()
        order.status = "cancelled"
        order.save()

    return render(request, "store/payment_cancel.html", {"order": order})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "store/order_success.html", {"order": order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "store/order_history.html", {"orders": orders})


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created — you're now logged in.")
            return redirect("product_list")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})
