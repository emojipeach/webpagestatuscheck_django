from django import forms

class SearchForm(forms.Form):
    submitted = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'class' : 'set-input-width is-center'}))
