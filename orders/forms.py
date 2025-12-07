from django import forms


class CheckoutForm(forms.Form):
    """
    Форма оформления заказа.

    Содержит персональные данные покупателя, адрес доставки,
    комментарий к заказу и метод оплаты.
    """

    # --- Основные поля ---
    full_name = forms.CharField(
        max_length=255,
        label="ФИО",
    )

    email = forms.EmailField(
        required=False,
        label="Email",
    )

    phone = forms.CharField(
        required=True,
        label="Телефон",
    )

    shipping_address = forms.CharField(
        required=True,
        max_length=500,
        label="Адрес доставки",
        widget=forms.Textarea(attrs={"rows": 2}),
    )

    comment = forms.CharField(
        required=False,
        label="Комментарий",
        widget=forms.Textarea(attrs={"rows": 2}),
    )

    # --- Способы оплаты ---
    PAYMENT_CHOICES = [
        ("cash", "Наличными при получении"),
        ("card", "Банковская карта"),
        ("cod", "Оплата при получении (COD)"),     # нужно для тестов
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        required=True,
        label="Способ оплаты",
        widget=forms.RadioSelect,
    )

    # --- Валидация обязательных полей ---

    def clean_full_name(self):
        value = self.cleaned_data.get("full_name", "").strip()
        if not value:
            raise forms.ValidationError("Поле обязательно.")
        return value

    def clean_shipping_address(self):
        value = self.cleaned_data.get("shipping_address", "").strip()
        if not value:
            raise forms.ValidationError("Поле обязательно.")
        return value

    def clean_phone(self):
        value = self.cleaned_data.get("phone", "").strip()
        if not value:
            raise forms.ValidationError("Поле обязательно.")
        return value
