from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=200, label="Full name")
    address = forms.CharField(
        max_length=300,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Shipping address",
    )


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} star{'s' if i != 1 else ''}") for i in range(1, 6)]),
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "Share your thoughts about this product..."}),
        }
