from django.urls import path
from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("product/<int:pk>/review/", views.submit_review, name="submit_review"),

    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:pk>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),

    path("checkout/", views.checkout, name="checkout"),
    path("checkout/razorpay/<int:order_id>/", views.razorpay_checkout, name="razorpay_checkout"),
    path("payment/mock/<int:order_id>/", views.mock_payment_process, name="mock_payment_process"),
    path("payment/verify/<int:order_id>/", views.payment_verify, name="payment_verify"),
    path("payment/failed/<int:order_id>/", views.payment_failed, name="payment_failed"),
    path("order/success/<int:order_id>/", views.order_success, name="order_success"),
    path("orders/", views.order_history, name="order_history"),

    path("register/", views.register, name="register"),
]
