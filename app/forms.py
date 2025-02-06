from django import forms
from .models import *


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['first_name', 'last_name', 'phone', 'email', 'address1', 'address2', 'country', 'city', 'state']


class ProductFilter(forms.Form):
    min_price = forms.DecimalField(required=False, label='Min price', decimal_places=2)
    max_price = forms.DecimalField(required=False, label='Max price', decimal_places=2)

    def filter_price(self, queryset):
        if self.cleaned_data['min_price']:
            queryset = queryset.filter(price__gte=self.cleaned_data['min_price'])
        if self.cleaned_data['max_price']:
            queryset = queryset.filter(price__gte=self.cleaned_data['max_price'])

        return queryset