from django import forms

class SimilarityForm(forms.Form):
    input_sentence = forms.CharField(label='Enter a sentence', max_length=1000)
