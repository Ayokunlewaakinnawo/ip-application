# forms.py
from django import forms

class QuoteRequestForm(forms.Form):
    notes = forms.CharField(widget=forms.Textarea, required=False)
    comments = forms.CharField(widget=forms.Textarea, required=False)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    company = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20)
    email = forms.EmailField()
    item_id = forms.IntegerField()
    quantity = forms.IntegerField(min_value=1)



class QuoteRequestFormCart(forms.Form):
    notes = forms.CharField(widget=forms.Textarea, required=False)
    comments = forms.CharField(widget=forms.Textarea, required=False)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    company = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20)
    email = forms.EmailField()
