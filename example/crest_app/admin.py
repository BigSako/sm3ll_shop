from django.contrib import admin

# Register your models here.
from .models import EveUser, EveUserProfile


# add profile and users to admin
admin.site.register(EveUser)

class EvEUserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('profile_created_at','profile_updated_at',)

admin.site.register(EveUserProfile,EvEUserProfileAdmin)
