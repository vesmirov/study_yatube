from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста', 
            'group': 'Группа', 
            'image': 'Изображение',
        }
        error_messages = {'image': {'invalid': 'invalid type'}
        }
        help_texts = {'text': 'Добавьте текст',}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {'text': 'Добавьте комментарий'}
