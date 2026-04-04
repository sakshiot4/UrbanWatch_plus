from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        # We include the hidden map fields here so the form accepts them
        fields = ['title', 'description', 'category', 'latitude', 'longitude', 'region', 'pincode', 'location', 'proof_image']
        
        widgets = {
            'category': forms.Select(attrs={'class': 'select select-bordered w-full bg-white border-gray-300'}),
            # We keep region in the fields so the backend can save it, 
            # but we can hide it from the UI or make it optional
            'region': forms.Select(attrs={'class': 'hidden'}), 
        }
        
        labels= {
            'title': 'Complaint Title',
            'description': 'Description',
            'category': 'Category',
            'proof_image': 'Upload Proof Image',
        }

    def __init__(self, *args, **kwargs):
        super(ComplaintForm, self).__init__(*args, **kwargs)
        # --- CRITICAL FIX ---
        # These fields are now handled by the Map/JS/Backend logic, 
        # so we tell the form they are NOT required to be filled by the user manually.
        self.fields['location'].required = False
        self.fields['region'].required = False
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.fields['pincode'].required = False


# Add this at the bottom of complaints/forms.py
class ComplaintEditForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'description', 'category', 'proof_image']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input input-bordered w-full bg-slate-50 mt-1'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full bg-slate-50 mt-1',
                'rows': 4
            }),
            'category': forms.Select(attrs={
                'class': 'select select-bordered w-full bg-slate-50 mt-1'
            }),
        }