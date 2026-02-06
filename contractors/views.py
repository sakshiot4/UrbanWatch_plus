from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction #
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

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
    # 1. Active: Assigned/In Progress AND (No feedback OR feedback is empty string)
    active_complaints = Complaint.objects.filter(
        contractor=contractor,
        status__in=['assigned', 'in_progress']
    ).filter(
        Q(officer_feedback__isnull=True) | Q(officer_feedback="")
    ).select_related('citizen').order_by('-updated_at')

    # 2. Rejected: In Progress AND (Has feedback AND feedback is NOT empty string)
    rejected_complaints = Complaint.objects.filter(
        contractor=contractor,
        status='in_progress',
        officer_feedback__isnull=False
    ).exclude(officer_feedback="").select_related('citizen').order_by('-updated_at')

    #Completed work.
    verification_complaints = Complaint.objects.filter(
        contractor = contractor,
        status__in = ['completed']
    ).select_related('officer', 'citizen').order_by('-updated_at')

    closed_complaints = Complaint.objects.filter(
        contractor=contractor,
        status='closed'
    ).select_related('officer').order_by('-closed_at')

    #paginate active complaints.
    pagination = Paginator(active_complaints, 5) 
    page = request.GET.get('page')
    active_page = pagination.get_page(page)

    context = {
        'contractor': contractor,
        'active_complaints': active_page,
        # 'active_complaints': active_complaints,
        'verification_complaints': verification_complaints,
        'closed_complaints': closed_complaints,
        'rejected_complaints': rejected_complaints,
        
        # Counts for badges
        'active_count': active_complaints.count(),
        'verification_count': verification_complaints.count(),
        'closed_count': closed_complaints.count(),
        'rejected_count': rejected_complaints.count(),
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
    
    # Lock the row for update to prevent race conditions
    complaint = Complaint.objects.select_for_update().get(id=complaint_id)
    current_status = complaint.status

    # Security Checks
    if complaint.contractor != contractor:
        messages.error(request, "You are not assigned to this complaint.")
        return redirect('contractors:contractor_dashboard')
    
    if complaint.status not in ['assigned', 'in_progress']:
        messages.error(request, "You cannot update the status of this complaint.")
        return redirect('contractors:contractor_complaint_detail', complaint_id=complaint.id)
    
    if request.method == 'POST':
        form = ContractorStatusUpdateForm(request.POST, request.FILES, instance=complaint)
        
        if form.is_valid():
            new_status = form.cleaned_data['status']
            uploaded_image = form.cleaned_data.get('completion_image')

            # --- LOGIC FIX: Auto-detect completion ---
            # If currently 'In Progress' and they upload an image, force status to 'Completed'
            # (This handles cases where the dropdown/hidden field might still say 'In Progress')
            if current_status == 'in_progress' and uploaded_image:
                new_status = 'completed'

            # Check if nothing changed (only if no image was uploaded)
            if new_status == current_status and not uploaded_image:
                messages.info(request, "No status change detected.")
                return redirect('contractors:contractor_complaint_detail', complaint_id=complaint.id)

            # --- CASE 1: STARTING WORK (Assigned -> In Progress) ---
            if current_status == 'assigned' and new_status == 'in_progress':
                complaint = form.save(commit=False)
                complaint.status = 'in_progress'
                if not complaint.in_progress_at:
                    complaint.in_progress_at = timezone.now()
                complaint.save()
                messages.success(request, "Work started! Status is now In Progress.")

            # --- CASE 2: FINISHING WORK (In Progress -> Completed) ---
            elif current_status == 'in_progress' and new_status == 'completed':
                
                # Validation: Image is mandatory for completion
                has_image = uploaded_image or complaint.completion_image
                if not has_image:
                    messages.error(request, "⚠️ You must upload a 'Proof of Work' image to mark this as Completed.")
                    return redirect('contractors:contractor_complaint_detail', complaint_id=complaint.id)

                complaint = form.save(commit=False)
                complaint.status = 'completed'
                complaint.completed_at = timezone.now()
                
                # Clear any previous feedback since they are resubmitting
                complaint.officer_feedback = None 
                
                complaint.save()
                messages.success(request, "Proof uploaded! Work marked as completed and sent for review.")

            # --- CASE 3: INVALID TRANSITION ---
            else:
                messages.error(request, f"Invalid status change: Cannot go from {current_status} to {new_status}.")

        else:
            messages.error(request, "Form error. Please check your inputs.")

    return redirect('contractors:contractor_complaint_detail', complaint_id=complaint.id)



#for officers to choose contractors for complaints.
# contractors/views.py

# contractors/views.py

@login_required
def contractor_list_for_complaint(request, complaint_id):
    """
    List contractors for an officer to choose for a specific complaint.
    """
    try:
        officer = Officer.objects.get(user=request.user)
    except Officer.DoesNotExist:
        messages.error(request, "Officer profile not found.")
        return redirect('home')
    
    complaint = get_object_or_404(Complaint, id=complaint_id) 

    if complaint.officer != officer:
        messages.error(request, "You are not assigned to this complaint.")
        return redirect('officers:officer_dashboard')
    
    # --- DEBUGGING PRINTS (Check your terminal!) ---
    print(f"--- LOOKING FOR CONTRACTORS ---")
    print(f"Complaint Region: {complaint.region}")
    print(f"Complaint Category (Speciality): {complaint.category}")
    
    # 1. Try finding just by Region first to see if that works
    region_match = Contractor.objects.filter(region=complaint.region, status='approved').count()
    print(f"Contractors in this Region (Approved): {region_match}")

    # 2. Try strict matching
    contractors = Contractor.objects.filter(
        status='approved',
        region=complaint.region,
        specialization=complaint.category 
    ).order_by('name')

    print(f"Strict Matches Found: {contractors.count()}")
    print("--------------------------------")

    # Pagination
    paginator = Paginator(contractors, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'officer': officer,
        'complaint': complaint,
        'contractors': page_obj,
        'is_paginated': page_obj.has_other_pages,
        'page_obj': page_obj,
    }

    return render(request, 'contractors/contractor_list_for_complaint.html', context)