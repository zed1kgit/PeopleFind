from django import forms

from topics.models import Topic, Comment
from Interests.forms import StyleFormMixin


class TopicForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'description']
