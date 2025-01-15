from django import forms

class ReturnRequestForm(forms.Form):
    order_id = forms.IntegerField(widget=forms.HiddenInput())
    reason = forms.ChoiceField(choices=[
        ('Damaged Product', 'Damaged Product'),
        ('Wrong Item', 'Wrong Item'),
        ('Quality Issue', 'Quality Issue'),
        ('Other', 'Other')
    ])
    comment = forms.CharField(widget=forms.Textarea, required=False)
