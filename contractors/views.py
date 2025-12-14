from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction #
from django.contrib import messages
from django.core.paginator import Paginator

from officers.models import Officer
from officers.forms import StatusUpdateForm #

from complaints.models import Complaint

from .models import Contractor
from .forms import ContractorStatusUpdateForm

@login_required
def pending_approval(request):
    """Show pending screen"""
    return render(request, 'contractors/pending_approval.html')

@login_required
def application_rejected(request):
    """Show rejected screen with reason"""
    try:
        contractor = request.user.contractor_profile
        reason = contractor.rejection_reason
    except:
        reason = "No reason provided."
    return render(request, 'contractors/rejected.html', {'reason': reason})

@login_required
def contractor_dashboard(request):
    """Conttractor dashboard shwoing assigned complaints."""
    try:
        contractor = Contractor.objects.get(user = request.user)
    except Contractor.DoesNotExist:
        messages.error(request, "Contractor profile not found.")
        return redirect('home')
    
    #security check: Redirect if not apporval..
    if contractor.status == 'pending':
        return redirect('contractors:pending_approval')
    
    if contractor.status == 'rejected':
        return redirect('contractors:application_rejected')
    
    #Active work : assigned or in_progress.
    active_complaints = Complaint.objects.filter(
        contractor= contractor,
        status__in = ['assigned', 'in_progress']
    ).select_related('officer', 'citizen').order_by('-created_at')

    #Completed work.
    completed_complaints = Complaint.objects.filter(
        contractor = contractor,
        status__in = ['completed', 'closed']
    ).select_related('officer', 'citizen').order_by('-created_at')

    #paginate active complaints.
    pagination = Paginator(active_complaints, 10) 
    page = request.GET.get('page')
    active_page = pagination.get_page(page)

    context = {
        'contractor': contractor,
        'active_complaints': active_page,
        'completed_complaints': completed_complaints,
        'active_count': active_complaints.count(),
        'completed_count': completed_complaints.count(),
    }

    return render(request,
                'contractors/contractor_dashboard.html', context)

@login_required
def contractor_complaint_detail(request, complaint_id):
    """View detailed information about a specific complaint assigned to the contractor."""
    try:
        contractor = Contractor.objects.get(user = request.user)
    except Contractor.DoesNotExist:
        messages.error(request, "Contractor profile not found.")
        return redirect('home')
    
    #Ensure the complaint exists and is assigned to this contractor.
    complaint = get_object_or_404(Complaint, id=complaint_id, contractor=contractor)

    #Check if contractor is assigned to this complaint.
    if complaint.contractor != contractor:
        messages.error(request, "You are not assigned to this complaint.")
        return redirect('contractors:contractor_dashboard')
    
    #only show status update form if complaint is assigned or in_progress.
    status_form = None
    if complaint.status in ['assigned', 'in_progress']:
        status_form = ContractorStatusUpdateForm(instance=complaint)

    context = {
        'contractor': contractor,
        'complaint': complaint,
        'status_form': status_form,
    }

    return render(request, 'contractors/contractor_complaint_detail.html', context)

@login_required
@transaction.atomic
def contractor_update_status(request, complaint_id):
    try:
        contractor = Contractor.objects.get(user=request.user)
    except Contractor.DoesNotExist:
        messages.error(request, "Contractor profile not found.")
        return redirect('home')
    
    complaint = Complaint.objects.select_for_update().get(id=complaint_id)
    
    # Store the current status BEFORE any changes
    current_status = complaint.status

    # Check if the contractor is assigned.
    if complaint.contractor != contractor:
        messages.error(request, "You are not assigned to this complaint.")
        return redirect('contractors:contractor_dashboard')
    
    # Check if the complaint is in a state contractor can update.
    if complaint.status not in ['assigned', 'in_progress']:
        messages.error(request, "You cannot update the status of this complaint.")
        return redirect('contractors:contractor_complaint_detail', complaint_id=complaint.id)
    
    if request.method == 'POST':
        form = ContractorStatusUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            new_status = form.cleaned_data['status']

            # Use current_status (before form), not complaint.status (which may change)
            if current_status == 'in_progress' and new_status == 'completed':
                complaint.status = 'completed'

                #set completed_at timesptamp if not already set.
                if complaint.completed_at is None:
                    complaint.completed_at = timezone.now()
                    
                complaint.save()
                messages.success(request, "Work marked as completed. Officer will review and close.")
            else:
                messages.error(request, f"Invalid status transition: {current_status} -> {new_status}")
        else:
            messages.error(request, "There was an error with the form. Please try again.")

    return redirect('contractors:contractor_complaint_detail', complaint_id=complaint_id)



#for officers to choose contractors for complaints.
@login_required
def contractor_list_for_complaint(request, complaint_id):
    """List contractors for an officer to choose for a specific complaint."""

    try:
        officer = Officer.objects.get(user = request.user)
    except Officer.DoesNotExist:
        messages.error(request, "Officer profile not found.")
        return redirect('home')
    
    # Ensure the complaint exists
    complaint = get_object_or_404(Complaint, id=complaint_id) 

    #Verify that the officer is assigned to this complaint
    if complaint.officer != officer:
        messages.error(request, "You are not assigned to this complaint.")
        return redirect('officers:officer_dashboard')
    
    #Get all contractors.
    contractors = Contractor.objects.all()

    context = {
        'officer': officer,
        'complaint': complaint,
        'contractors': contractors,
    }

    return render(request, 
                'contractors/contractor_list_for_complaint.html', context)
