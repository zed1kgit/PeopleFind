from django import forms

from Interests.models import Interest


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class InterestForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Interest
        fields = ('logo', 'name', 'description',)
