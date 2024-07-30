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


class QuoteAddon(forms.Form):
    quote_id = forms.CharField(max_length=100)
    address1 = forms.CharField(max_length=100)
    address2 = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    stateprov = forms.CharField(max_length=100)
    zip = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100, required=True)

    industry = forms.CharField(max_length=100, required=True)

    comments = forms.CharField(widget=forms.Textarea, required=False)
    purpose = forms.CharField(max_length=100, required=True)

class QuoteAddonInfo(forms.Form):
    response = forms.CharField(max_length=100, required=True)
    condition = forms.IntegerField()



class QuoteRequestFormCart(forms.Form):
    notes = forms.CharField(widget=forms.Textarea, required=False)
    comments = forms.CharField(widget=forms.Textarea, required=False)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    company = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20)
    email = forms.EmailField()
