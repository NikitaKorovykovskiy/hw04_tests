from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': ('Текст поста'),
            'group': ('Группы')
        }
        help_texts = {
            'text': ('Введите содержимое вашего поста'),
        }
