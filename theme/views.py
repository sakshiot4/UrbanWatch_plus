# 1. Import the Complaint model from your complaints app
from complaints.models import Complaint 

from django.shortcuts import render
from django.contrib import messages
import random


def home(request):
    # Initialize empty variables
    complaint = None
    timeline = []

    # Get all IDs, pick 3 random ones, then fetch those objects
    # This is more efficient than order_by('?') on large databases
    items = list(Complaint.objects.all()[:50]) # Get last 50 to pick from
    if len(items) > 3:
        random_complaints = random.sample(items, 3)
    else:
        random_complaints = items

    # Fetch the 3 most recently completed complaints for the "Wall of Fame"
    # We filter by status='completed' and order by the most recent first
    recent_resolves = Complaint.objects.filter(status='closed').order_by('-updated_at')[:3]

    # Fetch total fixed complaints count. For Stats section.
    total_fixed_count = Complaint.objects.filter(status__in=['closed', 'completed']).count()

    token = ""

    # 2. Check for POST (Form Submission) instead of GET
    if request.method == "POST":
        token = request.POST.get('token', '').strip()
        
        if token:
            try:
                # 3. Search Logic
                complaint = Complaint.objects.get(tracking_token=token)
                
                # 4. Your Timeline Logic (Copied from your snippet)
                timeline = [
                    {
                        'label': 'Submitted', 
                        'date': complaint.created_at, 
                        'completed': True, 
                        'desc': 'Complaint received.'
                    },
                    {
                        'label': 'Assigned', 
                        'date': complaint.assigned_at, 
                        'completed': bool(complaint.assigned_at), 
                        'desc': f'Officer assigned: {complaint.officer.name}' if complaint.officer else 'Waiting for assignment.'
                    },
                    {
                        'label': 'In Progress', 
                        'date': complaint.in_progress_at, 
                        'completed': bool(complaint.in_progress_at), 
                        'desc': 'Contractor is working.'
                    },
                    {
                        'label': 'Completed', 
                        'date': complaint.completed_at, 
                        'completed': bool(complaint.completed_at), 
                        'desc': 'Work finished & Proof uploaded.'
                    },
                    {
                        'label': 'Closed', 
                        'date': complaint.closed_at, 
                        'completed': bool(complaint.closed_at), 
                        'desc': 'Verified & Closed by Officer.'
                    },
                ]
            
            except (Complaint.DoesNotExist, ValueError):
                messages.error(request, "Invalid Tracking ID. Please check and try again.")
    
    # 5. Render the Homepage template
    return render(request, 'home.html', {
        'complaint': complaint,
        'timeline': timeline,
        'token': token,
        'recent_resolves': recent_resolves,
        'sample_tokens': random_complaints,
        'total_fixed': total_fixed_count,
    })