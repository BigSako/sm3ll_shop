import urllib2
from bz2file import BZ2File, BZ2Decompressor
import csv

from django.contrib import admin
from django.template.response import TemplateResponse
from django.conf.urls import include,url


# Register your models here.
from .models import InvType, ItemGroup, ItemMarketGroup



class IsPublishedFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Published?'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'published'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('1', 'Published'),
            ('0', 'Not Published'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == '1':
            return queryset.filter(published=1)
        if self.value() == '0':
            return queryset.filter(published=0)


class HasMarketGroupFilter(admin.SimpleListFilter):
    title = 'Market Group'

    parameter_name = 'itemmarketgroup'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('1', 'Can be bought on market'),
            ('0', 'Can not be bought on the market'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == '1':
            return queryset.filter(itemmarketgroup__isnull=False)
        if self.value() == '0':
            return queryset.filter(itemmarketgroup__isnull=True)



class ItemGroupAdmin(admin.ModelAdmin):
    """ Admin Settings for ItemGroup """
    list_display = ('groupID', 'groupName', 'is_published',)
    list_filter = (IsPublishedFilter, )


class MarketGroupAdmin(admin.ModelAdmin):
    """ Admin Settings for Market Group """
    list_display = ('marketGroupID', 'marketGroupName', 'description','parentGroupID',)
    list_filter = ('hasTypes','parentGroupID',)


class InvTypeGroupAdmin(admin.ModelAdmin):
    """ ADmin Settings for Item Type """
    list_display = ('typeID', 'typeName', 'itemgroup', 'itemmarketgroup', 'is_published',)
    list_filter = (IsPublishedFilter, HasMarketGroupFilter, )

# add profile and users to admin
#admin.site.register('self', MyModelAdmin)

admin.site.index_template = 'admin/custom_index.html'
admin.autodiscover()


admin.site.register(InvType, InvTypeGroupAdmin)
admin.site.register(ItemGroup, ItemGroupAdmin)
admin.site.register(ItemMarketGroup, MarketGroupAdmin)
