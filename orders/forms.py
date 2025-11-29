from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=255)
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)
    shipping_address = forms.CharField(max_length=500)
    comment = forms.CharField(required=False, widget=forms.Textarea)

    PAYMENT_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("card", "Card"),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        required=False,
        widget=forms.RadioSelect,
    )

    def clean_payment_method(self):
        value = self.cleaned_data.get("payment_method")
        if not value:
            return "cod"
        return value
