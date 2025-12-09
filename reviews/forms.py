from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]

        widgets = {
            "rating": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ваш комментарий…",
                    "rows": 4,
                }
            ),
        }

    def clean_comment(self):
        """Запрещаем отправлять полностью пустой комментарий."""
        comment = self.cleaned_data.get("comment", "").strip()
        if not comment:
            raise forms.ValidationError("Комментарий не может быть пустым.")
        return comment
