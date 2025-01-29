from django.urls import path
from . import views


urlpatterns = [
path("",views.product_list,name="products"),
path("add-to-cart/<int:product_id>/",views.add_to_cart,name='add_to_cart'),
path("view-cart/",views.view_cart,name='view_cart'),
path("order-confirmation/",views.order_confirmation,name='order_confirmation'),
path("order_success/",views.order_success,name="order_success"),
path("signup/",views.signup,name='signup'),
path("login/",views.user_login,name="login"),
path("logout/",views.user_logout,name="logout"),
path("remove-from-cart/<int:cart_item_id>/",views.remove_from_cart,name='remove_from_cart'),


]