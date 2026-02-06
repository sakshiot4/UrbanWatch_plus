from django.utils import timezone # For timestamping status changes.
from django.db import transaction # To ensure atomic updates
from django.shortcuts import render, redirect, get_object_or_404 # For rendering templates and handling redirects.
from django.contrib.auth.decorators import login_required # To restrict access to logged-in users.
from django.contrib import messages # For user feedback messages.
from django.core.paginator import Paginator # For paginating long lists.

from complaints.models import Complaint 

from contractors.models import Contractor
from django.utils import timezone

from .models import Officer 
from .forms import StatusUpdateForm, ContractorAssignmentForm

@login_required
def officer_dashboard(request):
    try:
        officer = Officer.objects.get(user=request.user)
    except Officer.DoesNotExist:
        messages.error(request, "Officer profile not found.")
        return redirect('home')

    # --- 1. TAKE ISSUES (Unassigned in Region) ---
    unassigned_qs = Complaint.objects.filter(
        region=officer.region, 
        officer__isnull=True
    ).order_by('-created_at')
    p_take = Paginator(unassigned_qs, 6)
    page_take = request.GET.get('page_take')
    take_issues = p_take.get_page(page_take)

    # --- 2. TAKEN ISSUES (Assigned/In Progress) ---
    taken_qs = Complaint.objects.filter(
        officer=officer, 
        status__in=['assigned', 'in_progress']
    ).select_related('contractor').order_by('-updated_at')
    p_taken = Paginator(taken_qs, 6)
    page_taken = request.GET.get('page_taken')
    taken_issues = p_taken.get_page(page_taken)

    # --- 3. VERIFICATION ISSUES (Completed, Pending Approval) ---
    verification_qs = Complaint.objects.filter(
        officer=officer, 
        status='completed'
    ).select_related('contractor').order_by('-completed_at')
    p_verify = Paginator(verification_qs, 6)
    page_verify = request.GET.get('page_verify')
    verification_issues = p_verify.get_page(page_verify)

    # --- 4. CLOSED ISSUES (History) ---
    closed_qs = Complaint.objects.filter(
        officer=officer, 
        status='closed'
    ).order_by('-closed_at')
    p_closed = Paginator(closed_qs, 6)
    page_closed = request.GET.get('page_closed')
    closed_issues = p_closed.get_page(page_closed)

    # Determine which tab should be active after a reload (e.g. clicking pagination)
    active_tab = 'take'
    if 'page_taken' in request.GET: active_tab = 'taken'
    elif 'page_verify' in request.GET: active_tab = 'verify'
    elif 'page_closed' in request.GET: active_tab = 'closed'

    context = {
        'officer': officer,
        'take_issues': take_issues,
        'taken_issues': taken_issues,
        'verification_issues': verification_issues,
        'closed_issues': closed_issues,
        'active_tab': active_tab,
        
        # Counts for Badges
        'count_take': unassigned_qs.count(),
        'count_taken': taken_qs.count(),
        'count_verify': verification_qs.count(),
        'count_closed': closed_qs.count(),
    }
    return render(request, 'officers/dashboard.html', context)


@login_required
@transaction.atomic
def assign_to_me(request, complaint_id):
    """Assign complaint to current officer with transaction lock."""
    try:
        officer = Officer.objects.get(user=request.user)
    except Officer.DoesNotExist:
        messages.error(request, "Officer profile not found.")
        return redirect('home')
    
    #Lock the row to prevent race conditions.
    complaint = Complaint.objects.select_for_update().get(id=complaint_id)

    if complaint.officer:
        messages.warning(request, "This complaint is already assigned to another officer.")
        return redirect('officers:dashboard')
    
    if complaint.region != officer.region:
        messages.error(request, "You can only assign complaints from your own region.")
        return redirect('officers:dashboard')
    
    complaint.officer = officer
    complaint.status = 'assigned'

    if complaint.assigned_at is None:
        complaint.assigned_at = timezone.now()

    complaint.save()

    messages.success(request, f"Complaint '{complaint.title}' assigned to you.")
    return redirect('officers:dashboard')

@login_required
def complaint_detail(request, complaint_id):
    """View and update/manage complaint details."""
    try:
        officer = Officer.objects.get(user=request.user)
    except Officer.DoesNotExist:
        messages.error(request, "Officer profile not found.")
        return redirect('home')
    
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if complaint.officer != officer:
        messages.error(request, "You are not assigned to this complaint.")
        return redirect('officers:dashboard')
    
    contractor_id = request.GET.get('contractor_id')
    if contractor_id:
        try:
            contractor = Contractor.objects.get(id=contractor_id)
            complaint.contractor = contractor 
        except Contractor.DoesNotExist:
            pass

    status_form = StatusUpdateForm(instance=complaint)
    
    # --- FILTERED DROPDOWN LOGIC ---
    contractor_form = ContractorAssignmentForm(instance=complaint)
    # Filter the 'contractor' field queryset based on complaint region and category
    contractor_form.fields['contractor'].queryset = Contractor.objects.filter(
        status='approved',
        region=complaint.region,
        specialization=complaint.category
    ).order_by('name')

    context = {
            'officer' : officer,
            'complaint' : complaint,
            'status_form' : status_form,
            'contractor_form' : contractor_form,
    }

    return render(request, 'officers/complaint_detail.html', context)

@login_required
def update_status(request, complaint_id):
    """Update the complaint status with validation."""

    try:
        officer = Officer.objects.get(user=request.user)
    except Officer.DoesNotExist:
        messages.error(request, "Officer profile not found.")
        return redirect('officers:dashboard')
    
    complaint = get_object_or_404(Complaint, id=complaint_id, officer=officer)

    if complaint.officer != officer:
        messages.error(request, "You are not assigned to this complaint.")
        return redirect('officers:dashboard')
    
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            new_status = form.cleaned_data['status']

            if not complaint.can_transition_to(new_status):
                messages.error(request, f"Cannot change status from {complaint.get_status_display()} to {dict(Complaint.STATUS_CHOICES)[new_status]}")
            else:
                #update the instance but don't save yet.
                complaint = form.save(commit=False)
                complaint.status = new_status

                #Set the appropriate timestamp once, when the status is first recahed.
                if new_status == 'assigned' and complaint.assigned_at is None:
                    complaint.assigned_at = timezone.now()
                if new_status == 'in_progress' and complaint.in_progress_at is None:
                    complaint.in_progress_at = timezone.now()
                if new_status == 'completed' and complaint.completed_at is None:
                    complaint.completed_at = timezone.now()
                if new_status == 'closed' and complaint.closed_at is None:
                    complaint.closed_at = timezone.now()
                complaint.save()
                messages.success(request, f"Complaint status updated to '{complaint.get_status_update()}'.")

        else:
            messages.error(request, "Invalid status update.")
            
    return redirect('officers:complaint_detail', complaint_id)

@login_required
@login_required
def assign_contractor(request, complaint_id):
    """Assign a contractor to the complaint."""
    try:
        officer = Officer.objects.get(user=request.user)
    except Officer.DoesNotExist:
        messages.error(request, "Officer profile not found.")
        return redirect('officers:dashboard')
    
    complaint = get_object_or_404(Complaint, id=complaint_id, officer=officer)

    if complaint.officer != officer:
        messages.error(request, "You are not assigned to this complaint.")
        return redirect('officers:dashboard')
    
    if request.method == 'POST':
        if 'remove_contractor' in request.POST:
            complaint.contractor = None
            if complaint.status == 'in_progress' and complaint.can_transition_to('assigned'):
                complaint.status = 'assigned'
            complaint.save()
            messages.success(request, "Contractor removed from complaint.")
            return redirect('officers:complaint_detail', complaint_id)
        
        form = ContractorAssignmentForm(request.POST, instance=complaint)
        
        # --- APPLY FILTER BEFORE VALIDATION ---
        form.fields['contractor'].queryset = Contractor.objects.filter(
            status='approved',
            region=complaint.region,
            specialization=complaint.category
        )

        if form.is_valid():
            complaint_obj = form.save(commit=False)
            if complaint_obj.contractor:
                if complaint_obj.can_transition_to('in_progress'):
                    complaint_obj.status = 'in_progress'
                    if complaint_obj.in_progress_at is None:
                        complaint_obj.in_progress_at = timezone.now()
                messages.success(request, f"Contractor '{complaint_obj.contractor.name}' assigned.")
            else:
                messages.info(request, "Contractor unassigned from complaint.")
            complaint_obj.save()
        else:
            messages.error(request, "Invalid contractor selection. Must be approved and match region/specialty.")
    
    return redirect('officers:complaint_detail', complaint_id)

@login_required
@transaction.atomic
def close_complaint(request, complaint_id):
    """Close a completed complaint - officer action"""
    try:
        officer = Officer.objects.get(user=request.user)
    except Officer.DoesNotExist:
        messages.error(request, "Officer profile not found.")
        return redirect('officers:dashboard')
    
    complaint = Complaint.objects.select_for_update().get(id=complaint_id)
    
    # Verify officer owns this complaint
    if complaint.officer != officer:
        messages.error(request, "You are not assigned to this complaint.")
        return redirect('officers:dashboard')
    
    # Can only close completed complaints
    if complaint.status != 'completed':
        messages.error(request, "Only completed complaints can be closed.")
        return redirect('officers:complaint_detail', complaint_id)
    
    # Close it
    complaint.status = 'closed'
    
    # Set closed_at timestamp
    if complaint.closed_at is None:
        complaint.closed_at = timezone.now()
    
    complaint.save()
    messages.success(request, "Complaint closed successfully!")
    return redirect('officers:complaint_detail', complaint_id)


@login_required
def contractor_approvals(request):
    """Officer view to approve/reject pending contractors"""
    try:
        officer = Officer.objects.get(user=request.user)
    except Officer.DoesNotExist:
        messages.error(request, "Officer profile not found.")
        return redirect('home')
    
    # Get pending contractors
    pending_contractors = Contractor.objects.filter(
        status='pending'
    ).order_by('-created_at')
    
    if request.method == 'POST':
        contractor_id = request.POST.get('contractor_id')
        action = request.POST.get('action')
        reason = request.POST.get('rejection_reason', '')
        
        contractor = get_object_or_404(Contractor, id=contractor_id)
        
        if action == 'approve':
            contractor.status = 'approved'
            contractor.approved_by = officer
            contractor.approved_at = timezone.now()
            contractor.save()
            messages.success(
                request,
                f"✓ Contractor {contractor.company_name} approved successfully."
            )
            
        elif action == 'reject':
            if not reason.strip():
                messages.error(request, "Please provide a reason for rejection.")
                return redirect('officers:contractor_approvals')
                
            contractor.status = 'rejected'
            contractor.rejection_reason = reason
            contractor.save()
            messages.warning(
                request,
                f"✕ Contractor {contractor.company_name} rejected."
            )
        
        return redirect('officers:contractor_approvals')
    
    context = {
        'officer': officer,
        'pending_contractors': pending_contractors,
    }
    return render(request, 'officers/contractor_approvals.html', context)


@login_required
@transaction.atomic
def reject_work(request, complaint_id):
    officer = get_object_or_404(Officer, user=request.user)
    complaint = get_object_or_404(
        Complaint.objects.select_for_update(),
        id=complaint_id,
        officer=officer
    )

    if request.method == 'POST':
        reason = request.POST.get('rejection_reason', '').strip()

        if not reason:
            messages.error(request, "Rejection reason is required.")
            return redirect('officers:complaint_detail', complaint.id)

        if not complaint.can_transition_to('in_progress'):
            messages.error(request, "Cannot reject work at this stage.")
            return redirect('officers:complaint_detail', complaint.id)

        complaint.status = 'in_progress'
        complaint.completed_at = None
        complaint.in_progress_at = timezone.now()
        complaint.officer_feedback = reason  # renamed field

        complaint.save()
        messages.warning(
            request,
            "Work rejected. Sent back to contractor for correction."
        )

    return redirect('officers:complaint_detail', complaint.id)
