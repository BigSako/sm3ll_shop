
import urllib2
from bz2file import BZ2Decompressor
import csv
import pycrest

from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from django.contrib.auth import logout as django_logout
from django.contrib.auth.views import login as django_login
from django.views.generic import TemplateView
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import admin
from django import forms
from django.template.response import TemplateResponse
from .context_processors import number_cart_items

from .models import InvType, ItemGroup, ItemMarketGroup, CartItem



def external_data_status(request):
    """ get the number of types in database (based on external sde) """
    context = dict(
        # Include common variables for rendering the admin template.
        admin.site.each_context(request),
        # Anything else you want in the context...
        type_cnt=InvType.objects.all().count(),
        item_group_cnt=ItemGroup.objects.all().count(),
        market_group_cnt=ItemMarketGroup.objects.all().count()
    )
    return TemplateResponse(request, "admin_market_data_status.html", context)



def external_data_update(request):
    """ update external data by dowloading them from fuzzwork, extracting the
    bzip and parsing the .csv file"""
    urls = [
            "https://www.fuzzwork.co.uk/dump/latest/invMarketGroups.csv.bz2",
            "https://www.fuzzwork.co.uk/dump/latest/invGroups.csv.bz2",
            #"https://www.fuzzwork.co.uk/dump/latest/invCategories.csv.bz2"
            "https://www.fuzzwork.co.uk/dump/latest/invTypes.csv.bz2",
            "https://www.fuzzwork.co.uk/dump/latest/invVolumes.csv.bz2",
]

    response_data = {}
    CHUNK = 16 * 1024

    update_item_list = []

    for url in urls:
        download = urllib2.urlopen(url)
        update_item_list.append(url)

        decompressor = BZ2Decompressor()

        response = ""

        while True:
            chunk = download.read(CHUNK)
            if not chunk: break

            decomp = decompressor.decompress(chunk)
            if decomp:
                response += decomp

        response_data[url] = response

        # now that this download is done, parse it
        csvfile = csv.DictReader(response.splitlines(), delimiter=',')
        # dispatch to the appropriate item type
        if "invGroups" in url:
            ItemGroup.parse(csvfile)
        elif "invVolumes" in url:
            continue # TODO: Implement this
        elif "invTypes" in url:
            InvType.parse(csvfile)
        elif "invMarketGroups" in url:
            ItemMarketGroup.parse(csvfile)
        elif "invCategories" in url:
            continue # TODO: Implement this
    # end for

    context = dict(
        # Include common variables for rendering the admin template.
        admin.site.each_context(request),
        # Anything else you want in the context...
        response_data=response_data,
        type_cnt=InvType.objects.all().count(),
        item_group_cnt=ItemGroup.objects.all().count(),
        market_group_cnt=ItemMarketGroup.objects.all().count()
    )

    return TemplateResponse(request,
                            "admin_market_data_update.html", context)



def render_extra(request, template, context):
    context['number_cart_items'] = number_cart_items(request)['number_cart_items']
    return render(request, template, context)



def search_market(request):
    search_param = request.GET.get('q', 'Damage Control')
    search_result = InvType.objects.filter(typeName__contains=search_param,published=1)

    context = dict(
        search_result=search_result,
        search_param=search_param
    )

    return render_extra(request, "show_search_result.html", context)


def show_item_detail(request, type_id):
    item=get_object_or_404(InvType, pk=type_id)

    context = dict(
        item=item,
        breadcrumbs=item.itemmarketgroup.get_parents_as_breadcrumb_list(include_self=True),
        market_data=get_crest_market_data(request, type_id=type_id)
    )
    return render_extra(request,
                            "show_item_detail.html", context)


def show_market_group(request, group_id):
    group = get_object_or_404(ItemMarketGroup, pk=group_id)
    sub_groups = ItemMarketGroup.objects.filter(parentGroupID=group_id)

    print("group=", group)

    if len(sub_groups) > 0:
        # there should not be any items in this group, display the sub_groups
        context = dict(
            group=group,
            breadcrumbs=group.get_parents_as_breadcrumb_list(),
            subgroups=sub_groups
        )

        return render(request, "show_market_subgroups.html", context)
    else:
        context = dict(
            group=group,
            breadcrumbs=group.get_parents_as_breadcrumb_list(),
            items=get_list_or_404(InvType,itemmarketgroup=group,published=1)
        )

        return render_extra(request, "show_market_group.html", context)


def add_item_to_cart(request, type_id):
    """ Adds an item to the cart and calls show_cart afterwards """
    # must be a post request, and therefore we verify the CSRF token
    if request.method == "POST":
        cur_eve_user = request.user.get_profile()
        itemtype = get_object_or_404(InvType, pk=type_id)
        CartItem.add_to_cart(cur_eve_user, itemtype, 1)

    return redirect("/cart") # show_cart(request)


def delete_item_from_cart(request, type_id):
    """ Removes an item from the cart and calls show_cart afterwards """
    cur_eve_user = request.user.get_profile()
    itemtype = get_object_or_404(InvType, pk=type_id)
    CartItem.remove_from_cart(cur_eve_user, itemtype)

    return redirect("/cart") # show_cart(request)

def show_cart(request):
    """ Shows the shopping cart of the current user """
    cur_eve_user = request.user.get_profile()
    # get all cart items for this user
    cart_items = CartItem.objects.filter(eveuser=cur_eve_user)

    context = dict(cart_items=cart_items,
                   )

    return render_extra(request, "show_cart.html", context)


def update_cart(request):
    if request.method == "POST": # we are receiving some data
        abc = 2
        form = forms.Form(request)
        # do something
        print(request)
        for item in form.data:
            print("form=",item)

    return redirect("/cart")


def get_crest_market_data(request, type_id):
    """fetch some market data from authenticated CREST"""

    # here we rudely fumble some of PyCrest's private parts
    # since we already completed the authentication process via python-social-auth
    authed_crest = pycrest.eve.AuthedConnection(
        res=request.user._get_crest_tokens(),
        endpoint=pycrest.EVE()._authed_endpoint,
        oauth_endpoint=pycrest.EVE()._oauth_endpoint,
        client_id=settings.SOCIAL_AUTH_EVEONLINE_KEY,
        api_key=settings.SOCIAL_AUTH_EVEONLINE_SECRET
    )
    authed_crest()

    # for demo purposes only: shortcut to market URL
    endpoint = pycrest.EVE()._authed_endpoint
    region_id = 10000002  # The Forge
    type_url = "{0}types/{1}/".format(endpoint, type_id)
    buy_orders_url = "{0}market/{1}/orders/buy/?type={2}".format(endpoint, region_id, type_url)
    sell_orders_url = "{0}market/{1}/orders/sell/?type={2}".format(endpoint, region_id, type_url)

    sell_orders = authed_crest.get(sell_orders_url)['items']
    buy_orders = authed_crest.get(buy_orders_url)['items']

    # sort by price up/down
    sell_orders = sorted(sell_orders, key=lambda k: k['price'])
    buy_orders = sorted(buy_orders, key=lambda k: k['price'], reverse=True)

    # truncate to Top <limit> orders
    limit = 5
    if len(sell_orders) > limit:
        sell_orders = sell_orders[0:limit]

    if len(buy_orders) > limit:
        buy_orders = buy_orders[0:limit]

    return {
        'sell_orders': sell_orders,
        'buy_orders': buy_orders
    }
