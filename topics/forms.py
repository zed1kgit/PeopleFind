from django import forms

from Interests.forms import StyleFormMixin
from topics.models import Topic


class TopicForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'description']
