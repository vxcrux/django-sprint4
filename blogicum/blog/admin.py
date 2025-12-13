from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Category, Comment, Location, Page, Post

User = get_user_model()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title", "description", "slug")
    list_editable = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("name",)
    list_editable = ("is_published",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "pub_date",
        "category",
        "author",
        "is_published",
        "created_at",
    )
    list_filter = ("pub_date", "category", "author", "is_published")
    search_fields = ("title", "text")
    list_editable = ("is_published",)
    autocomplete_fields = ("author", "category", "location")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "post",
        "author",
        "text",
        "created_at",
    )
    list_filter = (
        "post",
        "author",
    )
    search_fields = ("text",)
    list_editable = ()
    autocomplete_fields = ("post", "author")


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title", "content", "slug")
    list_editable = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}
