from django.contrib import admin
from .models import Users
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class CustomeUserAdmin(UserAdmin):
    model = Users
    list_display = ('username', 'name', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')  # 수정된 부분
    search_fields = ('email', 'name')
    ordering = ('email',)
    # filter_horizontal = ('groups', 'user_permissions')  # 수정된 부분

admin.site.register(Users, CustomeUserAdmin)