from django import forms
from complaints.models import Complaint
from contractors.models import Contractor

class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status']
        widgets = {
            'status': forms.Select
            (attrs = {'class': 'select select-bordered w-full'})
        } 

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            #only show the valid next statuses.
            if self.instance and self.instance.pk:
                current_status = self.instance.status
                valid_statuses = Complaint.STATUS_TRANSITIONS.get(current_status, [])
                self.fields['status'].choices = [
                    (status, label) for status, label in Complaint.STATUS_CHOICES
                    if status in valid_statuses or status == current_status
                ]

class ContractorAssignmentForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['contractor']
        widgets = {
            'contractor': forms.Select(
                attrs = {'class' : 'select select-bordered w-full'}
            )
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['contractor'].queryset = Contractor.objects.all()
            self.fields['contractor'].required = False
            