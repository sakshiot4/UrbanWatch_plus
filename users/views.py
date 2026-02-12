from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count  # NEEDED FOR BADGE COUNTS

from complaints.models import Complaint
from .models import Citizen
from .forms import UserUpdateForm, CitizenProfileForm, OfficerProfileForm, ContractorProfileForm



"""@login_required
def citizen_dashboard(request):
    #Citizen dashboard showing their submitted complaints.
    try:
        citizen = Citizen.objects.get(user = request.user)
    except Citizen.DoesNotExist:
        messages.error(request, "Citizen profile not found.")
        return redirect('account_sign')
    
    #get all complaints submitted by this citizen.
    all_complaints = Complaint.objects.filter(citizen = citizen).select_related('officer', 'contractor').order_by('-created_at')

    #Seperate status groups.
    pending_complaints = all_complaints.filter(status__in = ['reported', 'assigned', 'in_progress'])

    completed_complaints = all_complaints.filter(status__in = ['completed', 'closed'])

    #Pagination
    paginator = Paginator(pending_complaints, 5)
    page = request.GET.get('page')
    pending_page = paginator.get_page(page)

    context = {
        'citizen': citizen,
        'pending_complaints': pending_page,
        'completed_complaints': completed_complaints,
        'total_count': all_complaints.count(),
        'pending_count': pending_complaints.count(),
        'completed_count': completed_complaints.count(),
    }

    return render(request, 
                  "users/citizen_dashboard.html",
                    context)"""


@login_required
def citizen_dashboard(request):
    """
    Citizen dashboard with Tabs, Badges, and Pagination.
    """
    # --- 1. GET CITIZEN PROFILE (With Security Check) ---
    try:
        citizen = Citizen.objects.get(user=request.user)
    except Citizen.DoesNotExist:
        # Security: If a contractor tries to access this page, send them away
        if hasattr(request.user, 'contractor_profile'):
             return redirect('contractors:dashboard')
        
        messages.error(request, "Citizen profile not found. Please complete signup.")
        return redirect('account_signup')

    # --- 2. BASE QUERY (Optimized) ---
    # Fetch all complaints for this user, pre-fetching related data to avoid lag
    base_qs = Complaint.objects.filter(citizen=citizen).select_related('officer', 'contractor').order_by('-created_at')

    # 3. Get Counts for Badges
    # Result: {'reported': 5, 'closed': 12, ...}
    db_counts = base_qs.values('status').annotate(count=Count('status'))
    counts = {item['status']: item['count'] for item in db_counts}

    # --- 4. HANDLE TAB FILTERING ---
    # Get the active tab from the URL, default to 'reported' if nothing clicked
    active_tab = request.GET.get('status', 'reported')

    if active_tab == 'all':
        complaints_list = base_qs
    else:
        # Filter the list to show ONLY what matches the tab
        complaints_list = base_qs.filter(status=active_tab)

    # --- 5. PAGINATION ---
    # Show 6 items per page so the dashboard isn't endless
    paginator = Paginator(complaints_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'citizen': citizen,
        'page_obj': page_obj,       # The filtered, paginated list
        'active_tab': active_tab,   # To highlight the correct tab in CSS
        'counts': counts,           # The numbers for the badges
        'total_count': base_qs.count() # Total stats if needed
    }

    return render(request, "users/citizen_dashboard.html", context)

@login_required
def complaint_status_detail(request, complaint_id):

    """Citizen view their complaint status with the timeline"""
    try:
        citizen = Citizen.objects.get(user = request.user)
    except Citizen.DoesNotExist:
        messages.error(request, "Citizen profile not found.")
        return redirect('home')
    
    complaint = get_object_or_404(Complaint, id=complaint_id)

    #Verify the complaint belongs to the citizen.
    if complaint.citizen != citizen:
        messages.error(request, "You do not have permission to view this complaint.")
        return redirect('users:citizen_dashboard')
    
    #Build timeline.
    timeline = []

    #step 1: submitted.
    timeline.append({
        'status': 'reported', 
        'label': 'Submitted',
        'date': complaint.created_at,
        'completed': True,
        'description': f"Your complaint was submitted on {complaint.created_at.strftime('%Y-%m-%d %H:%M')}."
    })

    #Step 2: Assigned to Officer.
    timeline.append(
        {
            'status': 'assigned',
            'label': 'officer Assigned',
            'date': complaint.assigned_at,
            'completed': complaint.assigned_at is not None,
            'description': f"Officer {complaint.officer.name if complaint.officer else "Not assigned yet"} is handling your complaint."
        }
    )

    #Step 3:In Progress.
    timeline.append(
        {
            'status': 'in_progress',
            'label': 'Work in Progress',
            'date': complaint.in_progress_at,
            'completed': complaint.in_progress_at is not None,
            'description': f'{"Contractor " + complaint.contractor.name 
                              if complaint.contractor else "Contractor"} is working on your complaint.'
        }
    )

    # Step 4: Completed
    timeline.append({
        'status': 'completed',
        'label': 'Work Completed',
        'date': complaint.completed_at,
        'completed': complaint.completed_at is not None,
        'description': 'The work on your complaint has been completed',
    })

    # Step 5: Closed
    timeline.append({
        'status': 'closed',
        'label': 'Closed',
        'date': complaint.closed_at,
        'completed': complaint.closed_at is not None,
        'description': 'Your complaint has been verified and closed'
    })

    context = {
        'citizen': citizen,
        'complaint': complaint,
        'timeline': timeline,
    }

    return render(request, 'users/complaint_status_detail.html', context)

from .forms import UserUpdateForm, CitizenProfileForm, OfficerProfileForm, ContractorProfileForm

@login_required
def profile(request):
    user = request.user
    
    # --- 1. DETERMINE ROLE & SELECT FORM CLASS ---
    role = "Citizen"
    profile_data = None
    ProfileForm = CitizenProfileForm  # Default class

    if hasattr(user, 'officer_profile'):
        role = "Officer"
        profile_data = user.officer_profile
        ProfileForm = OfficerProfileForm
        
    elif hasattr(user, 'contractor_profile'):
        role = "Contractor"
        profile_data = user.contractor_profile
        ProfileForm = ContractorProfileForm
        
    elif hasattr(user, 'citizen_profile'):
        role = "Citizen"
        profile_data = user.citizen_profile
        ProfileForm = CitizenProfileForm

    # --- 2. HANDLE FORM SUBMISSION ---
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)
        # Initialize the selected form with data and files
        p_form = ProfileForm(request.POST, request.FILES, instance=profile_data)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your profile has been updated!')
            return redirect('users:profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileForm(instance=profile_data)

    # --- 3. DISPLAY INFO (For "View Mode") ---
    # We pass these to the template so we don't have to query logic there
    current_phone = getattr(profile_data, 'phone', '-')
    current_address = "-"
    
    if role == 'Citizen':
        current_address = getattr(profile_data, 'address', '-')
    elif role == 'Officer':
        current_address = f"{profile_data.get_region_display()} Region"
    elif role == 'Contractor':
        current_address = f"{profile_data.company_name} ({profile_data.get_region_display()})"

    # --- 4. STATS LOGIC (Keep your existing stats code exactly as is) ---
    stat_label_1 = "Reports Submitted"
    stat_label_2 = "Resolved Issues"
    total_count = 0
    success_count = 0

    if role == "Officer":
        stat_label_1 = "Cases Managed"
        stat_label_2 = "Cases Closed"
        total_count = Complaint.objects.filter(officer=user.officer_profile).count()
        success_count = Complaint.objects.filter(officer=user.officer_profile, status='closed').count()
    elif role == "Contractor":
        stat_label_1 = "Jobs Assigned"
        stat_label_2 = "Jobs Completed"
        total_count = Complaint.objects.filter(contractor=user.contractor_profile).count()
        success_count = Complaint.objects.filter(contractor=user.contractor_profile, status='completed').count()
    else: 
        total_count = Complaint.objects.filter(citizen__user=user).count()
        success_count = Complaint.objects.filter(citizen__user=user, status='closed').count()

    success_rate = 0
    if total_count > 0:
        success_rate = int((success_count / total_count) * 100)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'role': role,
        'current_phone': current_phone,
        'current_address': current_address,
        'stat_label_1': stat_label_1,
        'stat_label_2': stat_label_2,
        'total_count': total_count,
        'success_count': success_count,
        'success_rate': success_rate
    }

    return render(request, 'users/profile.html', context)