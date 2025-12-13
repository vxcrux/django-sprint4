from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

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


@login_required
def profile_edit(request):
    form = ProfileUpdateForm(request.POST or None, instance=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, 'Профиль успешно обновлен!')
        return redirect("blog:profile", username=request.user.username)
    
    context = {"form": form}
    return render(request, "blog/user.html", context) 
