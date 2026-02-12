from django import forms
from django.contrib.auth.models import User
from .models import Citizen
from officers.models import Officer
from contractors.models import Contractor

# 1. User Account Form (Name, Email)
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'last_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'email': forms.EmailInput(attrs={'class': 'input input-bordered w-full'}),
        }

# 2. Citizen Form (Phone, Address, Pic)
class CitizenProfileForm(forms.ModelForm):
    class Meta:
        model = Citizen
        fields = ['phone', 'address', 'profile_pic']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'address': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full h-24'}),
            'profile_pic': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
        }

# 3. Officer Form (Phone, Pic ONLY - Region is handled in template)
class OfficerProfileForm(forms.ModelForm):
    class Meta:
        model = Officer
        fields = ['phone', 'profile_pic']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'profile_pic': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
        }

# 4. Contractor Form (Phone, Pic ONLY - Specialization/Company are uneditable)
class ContractorProfileForm(forms.ModelForm):
    class Meta:
        model = Contractor
        fields = ['phone', 'profile_pic'] # Removed 'specialization' to make it uneditable
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'profile_pic': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
        }