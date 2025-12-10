from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ProfileUpdateForm

POSTS_PER_PAGE_USER_PROFILE = 10


def user_registration(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request,
                (f"Аккаунт для {username} создан! " "Теперь вы можете войти"),
            )
            return redirect("auth:login")
    else:
        form = UserCreationForm()

    context = {"form": form}
    return render(request, "registration/registration_form.html", context)


def profile(request, username):
    profile_object = get_object_or_404(User, username=username)

    if request.user.is_authenticated and request.user == profile_object:

        all_posts = profile_object.post_set.all().order_by("-pub_date")
    else:
        all_posts = profile_object.post_set.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        ).order_by("-pub_date")

    paginator = Paginator(all_posts, POSTS_PER_PAGE_USER_PROFILE)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "profile": profile_object,
        "page_obj": page_obj,
    }

    return render(request, "blog/profile.html", context)


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user)

    context = {"form": form}
    return render(request, "blog/user.html", context)
