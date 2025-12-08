from django import forms


class CheckoutForm(forms.Form):
    """
    Форма оформления заказа.

    Все обязательные поля валидируются вручную в clean_<field>,
    чтобы тесты могли находить строку «Поле обязательно.»
    """

    # --- Основные поля ---
    full_name = forms.CharField(
        max_length=255,
        label="ФИО",
        required=False,
    )

    email = forms.EmailField(
        required=False,
        label="Email",
    )

    phone = forms.CharField(
        required=False,
        label="Телефон",
    )

    shipping_address = forms.CharField(
        required=False,
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
        ("cod", "Оплата при получении (COD)"),  # важно для тестов
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        required=True,
        label="Способ оплаты",
        widget=forms.RadioSelect,
    )

    # --- Кастомная валидация обязательных полей ---

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
