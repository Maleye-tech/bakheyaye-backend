from django.contrib import admin

from .models import Category, Tenue, TenueImage


class TenueImageInline(admin.TabularInline):
    model = TenueImage
    extra = 1


@admin.register(Tenue)
class TenueAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "status", "is_favorite", "created_at")
    list_filter = ("status", "is_favorite", "category")
    search_fields = ("name", "fabric", "category__name")
    inlines = [TenueImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "position")
    list_editable = ("position",)
