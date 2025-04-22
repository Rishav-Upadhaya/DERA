from django import forms
from .models import property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = property
        fields = ['property_img', 'description', 'price', 'location' ]