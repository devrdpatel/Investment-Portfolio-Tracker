from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['portfolio', 'stock', 'quantity', 'purchase_price', 'purchase_date', 'order_type']

"""
    def clean_quantity(self):
        q = self.cleaned_data['quantity']
        if q <= 0:
            raise forms.ValidationError("Quantity must be positive.")
        return q        
"""