from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'description', 'category', 'location', 'region', 'proof_image']
        widgets = {
            'category': forms.Select(attrs={'class': 'select select-bordered w-1/2 bg-white border-gray-300'}),
            'region': forms.Select(attrs={'class': 'select select-bordered w-1/2 bg-white border-gray-300'}),
       }
        
        labels= {
                'title': 'Complaint Title',
                'description': 'Description',
                'category': 'Category',
                'location': 'Location',
                'region': 'Region',
                'proof_image': 'Upload Proof Image',
            }                   

        """widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter complaint title', }),
            'description': forms.Textarea(attrs={'placeholder': 'Describe your complaint', }),
            'category': forms.Select(attrs={'class': 'border-rounded'}),
            'location': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'region': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'proof_image': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
        }"""           

 