from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils import timezone

from .models import Roles


class RolesAdmin(admin.ModelAdmin):
    # 列表页配置
    list_display = ('name', 'desc', 'created_at', 'updated_at')
    list_display_links = ('name',)  # 使名称可点击进入编辑页
    search_fields = ('name', 'desc', 'prompt')  # 添加搜索字段
    list_filter = ('created_at', 'updated_at')  # 添加时间过滤器

    # 编辑页配置
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'desc')
        }),
        ('提示词配置', {
            'fields': ('prompt',),
            'classes': ('collapse',)  # 可折叠
        }),
        ('元数据', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    # 只读字段（自动设置的字段）
    readonly_fields = ('created_at', 'updated_at')

    # 自定义动作
    actions = ['duplicate_role']

    def duplicate_role(self, request, queryset):
        """复制角色动作"""
        for role in queryset:
            role.pk = None
            role.name = f"{role.name} (副本)"
            role.save()
        self.message_user(request, f"已成功复制 {queryset.count()} 个角色")

    duplicate_role.short_description = "复制选中角色"

    # 自定义保存方法
    def save_model(self, request, obj, form, change):
        """保存模型时自动更新更新时间"""
        if not change:  # 如果是新对象
            obj.created_at = timezone.now()
        obj.updated_at = timezone.now()
        super().save_model(request, obj, form, change)

    # 自定义列表页字段
    def get_desc_short(self, obj):
        """显示缩短的描述"""
        return obj.desc[:50] + '...' if len(obj.desc) > 50 else obj.desc

    get_desc_short.short_description = '描述'
    get_desc_short.admin_order_field = 'desc'

    def get_prompt_short(self, obj):
        """显示缩短的提示词"""
        return obj.prompt[:100] + '...' if len(obj.prompt) > 100 else obj.prompt

    get_prompt_short.short_description = '提示词'

    # 在列表页显示缩短的描述和提示词
    list_display = ('name', 'get_desc_short', 'get_prompt_short', 'created_at', 'updated_at')


admin.site.register(Roles, RolesAdmin)