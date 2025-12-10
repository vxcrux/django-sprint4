from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

MAX_LENGTH = 256


class BaseModel(models.Model):
    """Абстрактная модель"""

    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Добавлено"
    )

    class Meta:
        abstract = True


class Location(BaseModel):
    """Географическая метка"""

    name = models.CharField(
        max_length=MAX_LENGTH, verbose_name="Название места"
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Category(BaseModel):
    """Тематическая категория"""

    title = models.CharField(max_length=MAX_LENGTH, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        max_length=MAX_LENGTH,
        help_text=(
            "Идентификатор страницы для URL; разрешены символы латиницы, "
            "цифры, дефис и подчёркивание."
        ),
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Post(BaseModel):
    """Публикация"""

    title = models.CharField(max_length=MAX_LENGTH, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text=(
            "Если установить дату и время в будущем — "
            "можно делать отложенные публикации."
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
        related_name="posts",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Местоположение",
        related_name="posts",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория",
        null=True,
        blank=False,
        related_name="posts",
    )

    image = models.ImageField(
        upload_to="post_images/",
        null=True,
        blank=True,
        verbose_name="Изображение поста",
    )

    comment_count = models.IntegerField(default=0, editable=False)

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.title

    def update_comment_count(self):
        """Обновляет счетчик комментариев"""
        self.comment_count = self.comments.count()
        self.save(update_fields=["comment_count"])


class Comment(BaseModel):
    """Комментарий"""

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Текст комментария")

    class Meta(BaseModel.Meta):
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        is_creating = not self.pk
        super().save(*args, **kwargs)

        if is_creating:
            self.post.update_comment_count()


class Page(BaseModel):
    title = models.CharField(max_length=MAX_LENGTH, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, max_length=MAX_LENGTH)
    content = models.TextField(verbose_name="Содержимое")

    class Meta:
        verbose_name = "статичная страница"
        verbose_name_plural = "Статичные страницы"

    def __str__(self):
        return self.title
