from django import forms
from complaints.models import Complaint

class ContractorStatusUpdateForm(forms.ModelForm):
    """Form for the contractors to update status - limited options."""

    class Meta:
        model = Complaint
        fields = ['status', 'completion_image']
        widgets = {
            'status': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            #add styling to file input.
            'completion_image': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #Contractor can only move from in_progress to completed.
        if getattr(self, "instance", None) and self.instance.pk:
            current_status = self.instance.status

            #Only allow transition from in_progress to completed.
            if current_status == 'in_progress':
                allowed_statuses = ['in_progress', 'completed']
            elif current_status == 'assigned':
                allowed_statuses = ['assigned', 'in_progress']
            else:
                allowed_statuses = [current_status]

            #Filter STATUS_CHOICES based on allowed_statuses.
            self.fields['status'].choices = [
                (status, label) for status, label in Complaint.STATUS_CHOICES
                if status in allowed_statuses
            ]