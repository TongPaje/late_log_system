from django import forms
from .models import Student
import re

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['learner_reference_number', 'first_name', 'middle_name', 'last_name', 'year_level', 'section', 'qr_code']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        # Convert to uppercase
        first_name = first_name.upper()
        # Check if it contains numbers
        if any(char.isdigit() for char in first_name):
            raise forms.ValidationError("First name cannot contain numbers.")
        return first_name

    def clean_middle_name(self):
        middle_name = self.cleaned_data.get('middle_name', '')  # Default to empty string if None
        if middle_name:
            middle_name = middle_name.upper()  # Only call upper() if middle_name is not empty
        return middle_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        # Convert to uppercase
        last_name = last_name.upper()
        # Check if it contains numbers
        if any(char.isdigit() for char in last_name):
            raise forms.ValidationError("Last name cannot contain numbers.")
        return last_name

    def clean_section(self):
        section = self.cleaned_data.get('section')
        # Convert to uppercase
        section = section.upper()
        # Check if it contains numbers
        if any(char.isdigit() for char in section):
            raise forms.ValidationError("Section cannot contain numbers.")
        return section


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)