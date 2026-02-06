from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count  # NEEDED FOR BADGE COUNTS

from complaints.models import Complaint
from .models import Citizen



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