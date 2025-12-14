from django import forms
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm

from users.models import Citizen
from contractors.models import Contractor

class CitizenSignupForm(SignupForm):
    """Sign up form for citizens."""

    name = forms.CharField(max_length = 255, required = True,
                label='Full Name',
                widget=forms.TextInput(
                    attrs={'class':'input input-bordered w-full',
                           'placeholder': 'Your full name'}
                ))
    
    phone = forms.CharField(max_length=10, required=True,
        label='Phone Number',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': '10-digit phone number'
        }),
        help_text='10 digits only'
    )

    address = forms.CharField(
        max_length=255,
        required=True,
        label='Address',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Your residential address'
        })
    )

    region = forms.ChoiceField(
        required=True,
        label='Region',
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #Set region choices.
        self.fields['region'].choices = Citizen.REGION_CHOICES

        #Style inherited fields.
        self.fields['username'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Choose a username',
        })

        self.fields['email'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'your@email.com'
        })

        self.fields['password1'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Confirm password'
        })

    def clean_phone(self):
            phone = self.cleaned_data.get('phone')
            if phone and not phone.isdigit():
                raise forms.ValidationError('Phone number must contain only digits.')
            
            if phone and len(phone) != 10:
                raise forms.ValidationError('Phone number must be exactly 10 digits')
            
            return phone
        
    def save(self, request):
            user = super().save(request)

            #Create Citizen Profile.
            Citizen.objects.create(
                user=user,
                name=self.cleaned_data.get('name'),
                phone=self.cleaned_data.get('phone'),
                address=self.cleaned_data.get('address'),
                region=self.cleaned_data.get('region'),
            )

            return user
        
class ContractorSignupForm(SignupForm):
    """Signup form for Contractors."""

    name = forms.CharField(
        max_length=255,
        required=True,
        label='Full Name',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Your full name'
        })
    )

    company_name = forms.CharField(
        max_length=255,
        required=True,
        label='Company Name',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'e.g., ABC Repairs'
        })
    )

    phone = forms.CharField(
        max_length=10,
        required=True,
        label='Contact Phone',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': '10-digit phone number'
        }),
        help_text='10 digits only'
    )

    specialization = forms.ChoiceField(
        required=True,
        label='Specialization',
        choices=Contractor.CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        })
    )

    region = forms.ChoiceField(
        required=True,
        label='Service Region',
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        })
    )

    license_number = forms.CharField(
        max_length=100,
        required=True,
        label='License Number',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Your license number'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set region choices
        self.fields['region'].choices = Contractor.REGION_CHOICES
        
        # Style inherited fields
        self.fields['username'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Choose a username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'your@email.com'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Password'
        })

        self.fields['password2'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Confirm password'
        })

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise forms.ValidationError('Phone number must contain only digits')
        if phone and len(phone) != 10:
            raise forms.ValidationError('Phone number must be exactly 10 digits')
        return phone
            
    def save(self, request):
        user = super().save(request)
        
        # Create Contractor profile with "pending" status
        Contractor.objects.create(
            user=user,
            name=self.cleaned_data.get('name'),
            email=user.email,
            phone=self.cleaned_data.get('phone'),
            company_name=self.cleaned_data.get('company_name'),
            specialization=self.cleaned_data.get('specialization'),
            region=self.cleaned_data.get('region'),
            license_number=self.cleaned_data.get('license_number'),
            status='pending',  # Awaiting officer approval
        )
        
        return user