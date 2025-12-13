from django.urls import path, include

from . import views

app_name = "blog"

blog_core_urls = [
    path("", views.post_list, name="index"),
    path(
        "category/<slug:category_slug>/",
        views.post_list_by_category,
        name="category_posts",
    ),
    path("profile/<username>/", views.profile, name="profile"),
]

post_specific_urls = [
    path(
        "<int:post_id>/edit_comment/<int:comment_id>/edit/",
        views.edit_comment,
        name="edit_comment",
    ),
    path(
        "<int:post_id>/delete_comment/<int:comment_id>/delete/",
        views.delete_comment,
        name="delete_comment",
    ),
    path("<int:post_id>/edit/", views.post_edit, name="edit_post"),
    path("<int:post_id>/delete/", views.post_delete, name="delete_post"),
    path(
        "<int:post_id>/comment/", views.add_comment_to_post, name="add_comment"
    ),
    path("create/", views.post_create, name="post_create"),
    path("<int:post_id>/", views.post_detail, name="post_detail"),
]

urlpatterns = blog_core_urls + [
    path("posts/", include(post_specific_urls)),
]
