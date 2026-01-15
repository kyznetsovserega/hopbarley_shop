from __future__ import annotations

from django import forms

from products.models import Product


class ProductAdminForm(forms.ModelForm):
    """
    Форма управления продуктом в staff dashboard.
    """

    class Meta:
        model = Product
        fields = [
            "name",
            "short_description",
            "description",
            "unit",
            "price",
            "old_price",
            "category",
            "image",
            "is_active",
            "stock",
            "tags",
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "Input"}),
            "short_description": forms.Textarea(attrs={"class": "Textarea", "rows": 2}),
            "description": forms.Textarea(attrs={"class": "Textarea", "rows": 6}),
            "unit": forms.TextInput(attrs={"class": "Input"}),
            "price": forms.NumberInput(attrs={"class": "Input", "step": "0.01"}),
            "old_price": forms.NumberInput(attrs={"class": "Input", "step": "0.01"}),
            "category": forms.Select(attrs={"class": "Select"}),
            "stock": forms.NumberInput(attrs={"class": "Input", "min": "0"}),
            "tags": forms.TextInput(attrs={"class": "Input"}),
        }

    # Кастомная валидация
    def clean(self):
        cleaned = super().clean()
        price = cleaned.get("price")
        old_price = cleaned.get("old_price")

        if old_price and price and old_price <= price:
            raise forms.ValidationError("Старая цена должна быть больше текущей.")

        return cleaned
