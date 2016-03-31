from django.conf.urls import url

from . import views
from django.conf.urls import include,url
from django.contrib import admin


urlpatterns = [
    # market external sde thing
    url(r'^admin/market/external/',
        admin.site.admin_view(views.external_data_status), name='external_data_status'),
    url(r'^admin/market/external_update/',
        admin.site.admin_view(views.external_data_update), name='update_external_data'),
    url(r'^market/item/(?P<type_id>[0-9]+)', views.show_item_detail, name='show_item_info'),
    url(r'^market/group/(?P<group_id>[0-9]+)', views.show_market_group, name='show_market_group'),
    url(r'^market/search/', views.search_market, name='search_market'),
    url(r'^cart/$', views.show_cart, name='show_cart'),
    url(r'^cart/add/(?P<type_id>[0-9]+)', views.add_item_to_cart, name='cart_add'),
    url(r'^cart/update', views.update_cart, name='cart_update'),
    url(r'^cart/delete/(?P<type_id>[0-9]+)', views.delete_item_from_cart, name='cart_delete'),
]
