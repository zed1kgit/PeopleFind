from django import forms

from Interests.models import Interest


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'
    pass

class InterestForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Interest
        fields = ('logo', 'name', 'description',)
