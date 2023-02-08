from django.urls import path
from . import views


urlpatterns = [
    path('', views.Blog, name='Blog'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('register_page/', views.registerPage, name="register_page"),
    path('login_page/', views.loginPage, name="login_page"),
    path('logout_page/', views.logoutUser, name='logout_page'),
    path('blog_page/', views.blogPage, name='blog_page'),
    path('blog_post/<slug:slug>/', views.blog_post, name='blog_post'),
    path('<str:filepath>/', views.download_file, name='download_file')
]

