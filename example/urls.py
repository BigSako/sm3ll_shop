"""sm3ll_shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include,url
from django.contrib import admin

from django.contrib.auth.decorators import login_required
from crest_app.views import HomeView

admin.autodiscover()


urlpatterns = [
    url(r'^$', login_required(HomeView.as_view(), redirect_field_name=None)),
    url(r'^login/$', 'example.crest_app.views.login', name='user_login'),
    url(r'^logout/$', 'example.crest_app.views.logout', name='user_logout'),
    #url(r'^external_data/$', market.views.external_data_status, name='external_data_status'),
    #url(r'^external_data/update$', market.views.external_data_update, name='external_data_update'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', admin.site.urls),
    # append everything that is market related
    url('', include('example.market.urls', namespace='market')),
]
