from blog.models import Comment, Page, Post
from django import forms


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "text",
            "pub_date",
            "author",
            "location",
            "category",
            "image",
            "is_published",
        ]

        exclude = ("author",)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Ваш комментарий"}
            ),
        }


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ["title", "slug", "content", "is_published"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 15}),
        }
