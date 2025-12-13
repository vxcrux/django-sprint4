from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("blog.urls", namespace="blog")),
    path("pages/", include("pages.urls")),
    path("auth/", include("users.urls", namespace="users")),
    path(
        "auth/registration/",
        include(("django.contrib.auth.urls", "auth"), namespace="auth"),
    ),
    path("login/", include("django.contrib.auth.urls")),
]

handler404 = "pages.views.custom_404"
handler500 = "pages.views.custom_500"

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
