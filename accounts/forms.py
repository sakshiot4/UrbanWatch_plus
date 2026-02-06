from django import forms
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from users.models import Citizen
from contractors.models import Contractor
import re


class CitizenSignupForm(SignupForm):
    # 1. Account Fields
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Choose a unique username',
            'class': 'form-input' # We style this class in CSS below
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'name@example.com',
            'class': 'form-input'
        })
    )
    password1 = forms.CharField(
        label="Password",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Min. 8 characters',
            'class': 'form-input'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Re-enter password',
            'class': 'form-input'
        })
    )

    # 2. Personal Fields
    name = forms.CharField(
        max_length=100,
        label="Full Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Rahul Sharma',
            'class': 'form-input'
        })
    )
    phone = forms.CharField(
        max_length=10,
        min_length=10,
        label="Phone Number",
        help_text="10-digit mobile number",
        widget=forms.TextInput(attrs={
            'placeholder': '9876543210',
            'pattern': '[0-9]{10}', # HTML5 validation for 10 digits
            'title': 'Please enter a valid 10-digit mobile number',
            'class': 'form-input'
        })
    )
    region = forms.ChoiceField(
        choices=[('', 'Select your Ward/Zone')] + [('ward_a', 'Ward A (Colaba)'), ('ward_b', 'Ward B (Bandra)'), ('ward_c', 'Ward C (Andheri)')], # Update with your real choices
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Flat No, Building, Street...',
            'rows': 3,
            'class': 'form-input'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 1. Populate Region choices from the Model
        self.fields['region'].choices = Citizen.REGION_CHOICES
        
        # 2. Style the default Allauth fields (username, email, password)
        # We don't need to define them above, Allauth adds them automatically.
        # We just add CSS classes here.
        for field in ['username', 'email', 'password1', 'password2']:
            if field in self.fields:
                self.fields[field].widget.attrs.update({
                    'class': 'input input-bordered w-full'
                })
                
    def save(self, request):
        """
        The Master Save Method.
        1. Saves the User (Auth Table)
        2. Saves the Citizen (Profile Table)
        """
        # 1. Let Allauth create the User object first
        user = super().save(request)

        # 2. Create the linked Citizen Profile
        Citizen.objects.create(
            user=user,
            name=self.cleaned_data['name'],
            phone=self.cleaned_data['phone'],
            address=self.cleaned_data['address'],
            region=self.cleaned_data['region']
        )
        
        # 3. Return the user object (Required by Allauth)
        return user
    # --- CUSTOM VALIDATIONS ---

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if User.objects.filter(email=email).exists():
    #         raise forms.ValidationError("An account with this email already exists.")
    #     return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^\d{10}$', phone):
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Passwords do not match.")


from django import forms
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from users.models import Citizen
from contractors.models import Contractor
import re

# ... (CitizenSignupForm remains the same) ...

class ContractorSignupForm(SignupForm):
    """Signup form for Contractors with strict validation."""

    # --- 1. LOGIN FIELDS (Must be explicit for custom styling) ---
    username = forms.CharField(
        max_length=150, required=True,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Username'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Confirm Password'})
    )

    # --- 2. BUSINESS FIELDS ---
    name = forms.CharField(
        max_length=255, required=True,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Full Name'})
    )

    company_name = forms.CharField(
        max_length=255, required=True,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Company Name'})
    )

    phone = forms.CharField(
        max_length=10, required=True,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': '10-digit Contact'})
    )

    specialization = forms.ChoiceField(
        required=True,
        choices=Contractor.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'})
    )

    region = forms.ChoiceField(
        required=True,
        # Ensure your Contractor model uses REGION_CHOICES (plural)
        choices=Contractor.REGION_CHOICES, 
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'})
    )

    license_number = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'License ID'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Explicitly set choices to ensure they load
        self.fields['region'].choices = Contractor.REGION_CHOICES

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError('Use digits only.')
        if Contractor.objects.filter(phone=phone).exists():
            raise forms.ValidationError('This phone number is already in use by another contractor.')
        return phone

    def clean_license_number(self):
        lic = self.cleaned_data.get('license_number')
        if Contractor.objects.filter(license_number=lic).exists():
            raise forms.ValidationError('This license number is already registered in our system.')
        return lic

    # --- THE CRITICAL FIX ---
    # Renamed from 'try_save' to 'save' so the view calls it correctly
    def save(self, request):
        # 1. Let Allauth create the User (Auth Table)
        user = super().save(request)
        
        # 2. Create the Contractor Profile (Profile Table)
        Contractor.objects.create(
            user=user,
            name=self.cleaned_data.get('name'),
            email=user.email,
            phone=self.cleaned_data.get('phone'),
            company_name=self.cleaned_data.get('company_name'),
            specialization=self.cleaned_data.get('specialization'),
            region=self.cleaned_data.get('region'),
            license_number=self.cleaned_data.get('license_number'),
            status='pending', 
        )
        
        # 3. Return user (Required)
        return user