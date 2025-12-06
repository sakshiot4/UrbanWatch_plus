from django.db import transaction # To ensure atomic updates
from django.shortcuts import render, redirect, get_object_or_404 # For rendering templates and handling redirects.
from django.contrib.auth.decorators import login_required # To restrict access to logged-in users.
from django.contrib import messages # For user feedback messages.
from django.core.paginator import Paginator # For paginating long lists.
from complaints.models import Complaint 
from contractors.models import Contractor
from .models import Officer 
from .forms import StatusUpdateForm, ContractorAssignmentForm

@login_required
def officer_dashboard(request):
    """Officer dashboard showing region-specific unassigned and assigned complaints"""
    try:
        officer = Officer.objects.get(user=request.user)
    except Officer.DoesNotExist:
        messages.error(request, "Officer profile not found.")
        return redirect('home')
    
    # Filter by officer's region
    unassigned_complaints = Complaint.objects.filter(
        officer__isnull=True,
        status='reported',
        region=officer.region
    ).select_related('citizen', 'citizen__user').order_by('-created_at')
    
    # Paginate unassigned complaints
    paginator = Paginator(unassigned_complaints, 15)
    page = request.GET.get('page')
    unassigned_page = paginator.get_page(page)
    
   
    # My assigned complaints
    my_complaints = Complaint.objects.filter(
        officer=officer
    ).select_related('citizen', 'contractor').order_by('-updated_at')
    
    context = {
        'officer': officer,
        'unassigned_complaints': unassigned_page,
        'my_complaints': my_complaints,
        'officer_region': officer.get_region_display(),
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

    #Check if the officer is assigned to this complaint or it's unassigned in their region.
    if complaint.officer != officer:
        messages.error(request, "You are not assigned to this complaint.")
        return redirect('officers:dashboard')
    
    contractor_id = request.GET.get('contractor_id')
    if contractor_id:
        try:
            contractor = Contractor.objects.get(id=contractor_id)
            complaint.contractor = contractor #for form display only 
        except Contractor.DoesNotExist:
            pass

    status_form = StatusUpdateForm(instance=complaint)
    contractor_form = ContractorAssignmentForm(instance=complaint)

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
                form.save()
                messages.success(request, f"Complaint status updated to '{complaint.get_status_update()}'.")

        else:
            messages.error(request, "Invalid status update.")
            
    return redirect('officers:complaint_detail', complaint_id)

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
            # move status back
            if complaint.status == 'in_progress' and complaint.can_transition_to('assigned'):
                complaint.status = 'assigned'
            complaint.save()
            messages.success(request, "Contractor removed from complaint.")
            return redirect('officers:complaint_detail', complaint_id)
        
        form = ContractorAssignmentForm(request.POST, instance=complaint)
        if form.is_valid():
            complaint_obj = form.save(commit=False)
            if complaint_obj.contractor:
                #Auto set status to in_progress when contractor assigned.
                if complaint_obj.can_transition_to('in_progress'):
                    complaint_obj.status = 'in_progress'
                messages.success(request, f"Contractor '{complaint_obj.contractor.name}' assigned.")
            else:
                messages.info(request, "Contractor unassigned from complaint.")
            complaint_obj.save()
        else:
            messages.error(request, "Invalid contractor assignment.")
    
    return redirect('officers:complaint_detail', complaint_id)