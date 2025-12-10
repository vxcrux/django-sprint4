from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.index, name="index"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path(
        "pages/<slug:slug>/",
        views.PageDetailView.as_view(),
        name="page_detail",
    ),
    path("pages/", views.PageListView.as_view(), name="page_list"),
    path("pages/add/", views.PageCreateView.as_view(), name="page_create"),
    path(
        "pages/<slug:slug>/edit/",
        views.PageUpdateView.as_view(),
        name="page_edit",
    ),
    path(
        "pages/<slug:slug>/delete/",
        views.PageDeleteView.as_view(),
        name="page_delete",
    ),
    path(
        "category/" "<slug:category_slug>/",
        views.category_posts,
        name="category_posts",
    ),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("posts/create/", views.post_create, name="post_create"),
    path("posts/<int:pk>/edit/", views.post_edit, name="edit_post"),
    path("posts/<int:pk>/delete/", views.post_delete, name="delete_post"),
    path("post/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path(
        "posts/<int:post_id>/edit_comment/<int:comment_id>/",
        views.edit_comment,
        name="edit_comment",
    ),
    path(
        "posts/<int:post_id>/delete_comment/<int:comment_id>/",
        views.comment_delete,
        name="delete_comment",
    ),
]
