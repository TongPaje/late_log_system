# logs/forms.py
from django import forms
from .models import Student
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm

# User Registration Form with User Type (Student or Teacher)
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    user_type = forms.ChoiceField(choices=[('student', 'Student'), ('teacher', 'Teacher')])

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']

    def save(self, commit=True):
        user = super().save(commit=False)
        # Assign user type (student or teacher) as a custom field for later use
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user

class UserProfileEditForm(forms.ModelForm):
    user_type = forms.ChoiceField(choices=[('student', 'Student'), ('teacher', 'Teacher')])

    class Meta:
        model = User
        fields = ['username', 'email', 'user_type']

# Custom User Registration Form with manual password confirmation check
class CustomUserRegistrationForm(forms.Form):
    user_type_choices = [('student', 'Student'), ('teacher', 'Teacher')]
    user_type = forms.ChoiceField(choices=user_type_choices, widget=forms.RadioSelect, label="User Type")
    
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))
    password_confirmation = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        # Check if password and confirmation match
        if password != password_confirmation:
            raise forms.ValidationError("Password and confirmation do not match.")
        return cleaned_data

# Student registration form for adding student data
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['learner_reference_number', 'first_name', 'middle_name', 'last_name', 'year_level', 'section', 'qr_code', 'birthday', 'sex', 'address', 'parent_name', 'contact_number']

    # Define the sex field with RadioSelect widget
    sex = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female')],
        widget=forms.RadioSelect,  # Ensures that the form renders as radio buttons
        label="Sex"
    )

    # Validation for names and section to ensure no numbers are included
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        first_name = first_name.upper()
        if any(char.isdigit() for char in first_name):
            raise forms.ValidationError("First name cannot contain numbers.")
        return first_name

    def clean_middle_name(self):
        middle_name = self.cleaned_data.get('middle_name', '')
        if middle_name:
            middle_name = middle_name.upper()
        return middle_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        last_name = last_name.upper()
        if any(char.isdigit() for char in last_name):
            raise forms.ValidationError("Last name cannot contain numbers.")
        return last_name

    def clean_section(self):
        section = self.cleaned_data.get('section')
        section = section.upper()
        if any(char.isdigit() for char in section):
            raise forms.ValidationError("Section cannot contain numbers.")
        return section

    # Adding new validation fields
    birthday = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2025)), label="Birthday")
    address = forms.CharField(max_length=255, label="Address (Street/Purok, Barangay, Municipality, Province/City)")
    parent_name = forms.CharField(max_length=255, label="Parent/Guardian Name")
    contact_number = forms.CharField(
        max_length=11, 
        validators=[RegexValidator(r'^\d{11}$', 'Contact number must be exactly 11 digits.')],
        label="Contact Number"
    )

# Login form for user authentication
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
