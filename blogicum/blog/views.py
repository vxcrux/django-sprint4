from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
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


def get_posts_queryset(
    apply_publication_filters=True, include_annotation_and_ordering=False
):
    """Возвращает queryset объектов Post с различными настройками"""
    qs = Post.objects.select_related("author", "category", "location")

    if apply_publication_filters:
        qs = qs.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )

    if include_annotation_and_ordering:
        qs = qs.annotate(comment_count=Count("comments")).order_by("-pub_date")

    return qs


def paginate_queryset(
    queryset, per_page, request, num_links=POSTS_PER_PAGE_ON_INDEX
):
    """
    Создает и возвращает объект пагинатора для данного queryset
    num_links: Максимальное количество видимых ссылок на страницы в пагинации
    """
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


@login_required
def post_create(request):
    """Страница добавления новой публикации"""
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, f'Публикация "{post.title}" создана')
        return redirect("blog:profile", username=request.user.username)

    context = {"form": form}
    return render(request, "blog/create.html", context)


@login_required
def post_edit(request, post_id):
    """Редактирование существующей публикации"""
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        messages.error(request, "У вас нет прав на редактирование этого поста")
        return redirect("blog:post_detail", post_id=post.pk)

    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        messages.success(request, f'Публикация "{post.title}" обновлена')
        return redirect("blog:post_detail", post_id=post.pk)

    context = {"form": form}
    return render(request, "blog/create.html", context)


@login_required
def post_delete(request, post_id):
    """Удаление публикации"""
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        messages.error(request, "У вас нет прав на удаление этого поста")
        return redirect("blog:post_detail", post_id=post.pk)
    form = PostForm(request.POST or None, instance=post)
    if request.method == "POST":
        post.delete()
        messages.success(request, f'Пост "{post.title}" удален')
        return redirect("blog:profile", username=request.user.username)

    context = {"form": form}
    return render(request, "blog/detail.html", context)


def post_list(request):
    """
    Отображает главную страницу блога
    со списком последних публикаций с пагинацией
    """
    all_posts = get_posts_queryset(
        apply_publication_filters=True, include_annotation_and_ordering=True
    )
    page_obj = paginate_queryset(all_posts, POSTS_PER_PAGE_ON_INDEX, request)

    context = {"page_obj": page_obj}
    return render(request, "blog/index.html", context)


def post_detail(request, post_id):
    """Отображает полную информацию о публикации и её комментарии"""
    qs = Post.objects.select_related(
        "author", "category", "location"
    ).prefetch_related("comments", "comments__author")

    post = get_object_or_404(qs, pk=post_id)

    is_author = post.author == request.user
    is_hidden = (
        not post.is_published
        or not post.category.is_published
        or post.pub_date > timezone.now()
    )

    if not is_author and is_hidden:
        raise Http404("Post not found or access denied.")

    form = CommentForm(request.POST or None)
    comments = Comment.objects.select_related("author").filter(post=post)

    context = {
        "post": post,
        "form": form,
        "comments": comments,
    }
    return render(request, "blog/detail.html", context)


def post_list_by_category(request, category_slug):
    """Отображение публикаций в выбранной категории"""
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )

    all_posts = get_posts_queryset(
        apply_publication_filters=True, include_annotation_and_ordering=True
    ).filter(category=category)

    page_obj = paginate_queryset(all_posts, POSTS_PER_PAGE_ON_INDEX, request)

    context = {
        "category": category,
        "page_obj": page_obj,
    }
    return render(request, "blog/category.html", context)


def profile(request, username):
    """Отображение профиля пользователя с его публикациями"""
    profile_object = get_object_or_404(User, username=username)
    should_filter_published = request.user != profile_object

    all_posts = get_posts_queryset(
        apply_publication_filters=should_filter_published,
        include_annotation_and_ordering=True,
    ).filter(author=profile_object)

    page_obj = paginate_queryset(
        all_posts, POSTS_PER_PAGE_USER_PROFILE, request
    )

    context = {
        "profile": profile_object,
        "page_obj": page_obj,
    }
    return render(request, "blog/profile.html", context)


@login_required
def add_comment_to_post(request, post_id):
    """Обработка добавления комментария"""
    post = get_object_or_404(Post, pk=post_id)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        messages.success(request, "Комментарий добавлен")

    return redirect("blog:post_detail", post_id=post.pk)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария"""
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)

    if comment.author != request.user:
        messages.error(request, "Нет прав на редактирование этого комментария")
        return redirect("blog:post_detail", post_id=post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        messages.success(request, "Комментарий успешно обновлен")
        return redirect("blog:post_detail", post_id=post_id)

    context = {"form": form, "comment": comment}
    return render(request, "blog/comment.html", context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария"""
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    post = comment.post

    if comment.author != request.user:
        messages.error(request, "У вас нет прав на удаление этого комментария")
        return redirect("blog:post_detail", post_id=post.pk)

    if request.method == "POST":
        comment.delete()
        messages.success(request, "Комментарий успешно удален")
        return redirect("blog:post_detail", post_id=post.pk)

    context = {"comment": comment}
    return render(request, "blog/comment.html", context)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Миксин для проверки, является ли пользователь superuser.
    Используется для страниц, доступных только админу
    """

    def test_func(self):
        return self.request.user.is_superuser


class PageListView(StaffRequiredMixin, ListView):
    """Просмотр списка всех страниц"""

    model = Page
    template_name = "blog/page_list.html"
    context_object_name = "pages"
    queryset = Page.objects.filter(is_published=True).order_by("title")


class PageDetailView(DetailView):
    """Просмотр одной статичной страницы"""

    model = Page
    template_name = "blog/page_detail.html"
    context_object_name = "page"
    slug_field = "slug"

    def get_queryset(self):
        """
        Ограничивает доступ к неопубликованным страницам
        для тех, кто не superuser
        """
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            return qs.filter(is_published=True)
        return qs


class PageCreateView(StaffRequiredMixin, CreateView):
    """Создание новой статичной страницы"""

    model = Page
    form_class = PageForm
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:page_list")


class PageUpdateView(StaffRequiredMixin, UpdateView):
    """Редактирование статичной страницы"""

    model = Page
    form_class = PageForm
    template_name = "blog/create.html"
    slug_field = "slug"

    def get_success_url(self):
        """URL для перенаправления после успешного обновления"""
        return reverse_lazy(
            "blog:page_detail", kwargs={"slug": self.object.slug}
        )


class PageDeleteView(StaffRequiredMixin, DeleteView):
    """Удаление статичной страницы"""

    model = Page
    template_name = "blog/confirm_delete.html"
    slug_field = "slug"
    success_url = reverse_lazy("blog:page_list")

    def get_context_data(self, **kwargs):
        """Передача объекта страницы в контекст для шаблона подтверждения"""
        context = super().get_context_data(**kwargs)
        context["page"] = self.object
        context["action"] = "delete"
        return context
