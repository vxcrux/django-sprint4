from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, PageForm, PostForm
from .models import Category, Comment, Page, Post

User = get_user_model()

POSTS_PER_PAGE_ON_INDEX = 10
POSTS_PER_PAGE_USER_PROFILE = 10


def get_base_posts_queryset():
    """Возвращает список с базовыми фильтрами и select_related"""
    return Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).select_related("author", "category", "location")


@login_required
def post_create(request):
    """Страница добавления новой публикации"""
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, f'Публикация "{post.title}" создана')
            return redirect("blog:profile", username=request.user.username)
    else:
        form = PostForm()
    context = {"form": form, "title": "Создание публикации"}
    return render(request, "blog/create.html", context)


@login_required
def post_edit(request, pk):
    """Редактирование существующей публикации"""
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        messages.error(request, "У вас нет прав на редактирование этого поста")
        return redirect("blog:post_detail", post_id=post.pk)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, f'Публикация "{post.title}" обновлена')
            return redirect("blog:post_detail", post_id=post.pk)
    else:
        form = PostForm(instance=post)

    context = {"form": form, "action": "edit", "post": post}
    return render(request, "blog/create.html", context)


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        messages.error(request, "У вас нет прав на удаление этого поста")
        return redirect("blog:post_detail", post_id=post.pk)

    if request.method == "POST":
        post.delete()
        messages.success(request, f'Пост "{post.title}" удален')
        return redirect("blog:profile", username=request.user.username)

    context = {"post": post, "action": "delete_post_confirm"}
    return render(request, "blog/detail.html", context)


def index(request):
    """
    Отображает главную страницу блога
    со списком последних публикаций с пагинацией
    """
    all_posts = get_base_posts_queryset()

    paginator = Paginator(all_posts, POSTS_PER_PAGE_ON_INDEX)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}
    return render(request, "blog/index.html", context)


def post_detail(request, post_id):

    qs = Post.objects.select_related(
        "author", "category", "location"
    ).prefetch_related("comments")

    if request.user.is_authenticated:
        qs = qs.filter(Q(is_published=True) | Q(author=request.user))
    else:
        qs = qs.filter(is_published=True)
    try:
        post = get_object_or_404(qs, pk=post_id)
    except Http404:
        raise Http404("Post not found or access denied.")

    if (
        request.method == "POST"
        and "comment_submit" in request.POST
        and request.user.is_authenticated
    ):
        post.refresh_from_db()
        messages.success(request, "Комментарий добавлен")
        return redirect("blog:post_detail", post_id=post.pk)
    else:
        comment_form = CommentForm()

    context = {
        "post": post,
        "form": comment_form,
        "action": "viewing",
        "comments": post.comments.all(),
    }
    return render(request, "blog/detail.html", context)


def category_posts(request, category_slug):
    """Отображение публикаций в категории"""
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )

    all_posts = get_base_posts_queryset().filter(category=category)

    paginator = Paginator(all_posts, POSTS_PER_PAGE_ON_INDEX)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "category": category,
        "page_obj": page_obj,
    }
    return render(request, "blog/category.html", context)


def profile(request, username):

    profile_object = get_object_or_404(User, username=username)

    if request.user.is_authenticated and request.user == profile_object:
        all_posts = profile_object.posts.all().order_by("-pub_date")
    else:
        all_posts = profile_object.posts.filter(
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
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

            return redirect("blog:post_detail", post_id=post.pk)

    return redirect("blog:post_detail", post_id=post.pk)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)

    if comment.author != request.user:
        messages.error(request, "Нет прав на редактирование этого комментария")
        return redirect("blog:post_detail", post_id=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Комментарий успешно обновлен")
            return redirect("blog:post_detail", post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    context = {"form": form, "comment": comment, "action": "edit"}
    return render(request, "blog/comment.html", context)


@login_required
def comment_delete(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    post = comment.post

    if comment.author != request.user:
        messages.error(request, "У вас нет прав на удаление этого комментария")
        return redirect("blog:post_detail", post_id=post.pk)

    if request.method == "POST":
        comment.delete()
        messages.success(request, "Комментарий успешно удален")
        return redirect("blog:post_detail", post_id=post.pk)

    context = {"comment": comment, "post": post, "action": "delete"}
    return render(request, "blog/comment.html", context)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_superuser


class PageListView(StaffRequiredMixin, ListView):
    model = Page
    template_name = "blog/page_list.html"
    context_object_name = "pages"
    queryset = Page.objects.filter(is_published=True).order_by("title")


class PageDetailView(DetailView):
    model = Page
    template_name = "blog/page_detail.html"
    context_object_name = "page"
    slug_field = "slug"

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            return qs.filter(is_published=True)
        return qs


class PageCreateView(StaffRequiredMixin, CreateView):
    model = Page
    form_class = PageForm
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:page_list")


class PageUpdateView(StaffRequiredMixin, UpdateView):
    model = Page
    form_class = PageForm
    template_name = "blog/create.html"
    slug_field = "slug"

    def get_success_url(self):
        return reverse_lazy(
            "blog:page_detail", kwargs={"slug": self.object.slug}
        )


class PageDeleteView(StaffRequiredMixin, DeleteView):
    model = Page
    template_name = "blog/confirm_delete.html"
    slug_field = "slug"
    success_url = reverse_lazy("blog:page_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page"] = self.object
        context["action"] = "delete"
        return context
