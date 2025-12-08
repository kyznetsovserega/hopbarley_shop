from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]

        widgets = {
            "rating": forms.Select(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Ваш комментарий…",
                "rows": 3
            }),
        }
