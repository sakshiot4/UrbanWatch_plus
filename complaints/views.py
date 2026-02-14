from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from complaints.emails import send_alert
from complaints.models import Complaint
from .forms import ComplaintForm
from django.contrib import messages
from users.models import Citizen

from .utils import get_region_from_pincode #import the utility function


@login_required #a decorator to ensure only logged-in users can access
def submit_complaint(request): #this form allows citizens to submit complaints
    """View to handle complaint submission by citizens."""
    """print("🔥 VIEW CALLED!")  # Add this debug line
    print(f"User: {request.user}")
    print(f"Method: {request.method}")"""
    # Get citizen profile first (moved outside POST check)
    try: 
        citizen = Citizen.objects.get(user=request.user)
    except Citizen.DoesNotExist:
        messages.error(request, 'You must be registered as a citizen to submit complaints.')
        return redirect('home')
    
    if request.method == 'POST': #this checks if the form is submitted
        form = ComplaintForm(request.POST, request.FILES) #bind form with POST data and files
        if form.is_valid():     #validate the form data
            complaint = form.save(commit=False) #create complaint object but don't save to DB yet
            complaint.citizen = citizen #associate complaint with the logged-in citizen

            # GRAB DATA FROM HIDDEN INPUTS
            complaint.latitude = float(request.POST.get('latitude')) if request.POST.get('latitude') else None
            complaint.longitude = float(request.POST.get('longitude')) if request.POST.get('longitude') else None

            complaint.pincode = request.POST.get('pincode')
            complaint.location = request.POST.get('location') # This captures the full address

            # Auto-fill region based on pincode if provided
            pincode = request.POST.get('pincode') # We will send this from the frontend
            if pincode:
                complaint.pincode = pincode
                complaint.region = get_region_from_pincode(pincode).lower()
            else:
                complaint.region = 'central' #default region if no pincode

            complaint.status = 'reported'   #set initial status.
            complaint.save() #save complaint to DB.
           

            # --- 📧 NEW: SEND EMAIL TO CITIZEN ---
            # --- 📧 DEBUG EMAIL BLOCK ---
            print(f"--- ATTEMPTING EMAIL ---")
            print(f"User Email: '{request.user.email}'") # Check if this is empty!
            
            if request.user.email:
                subject = "Complaint Received"
                message = f"""
                Hello {request.user.first_name},

                We have successfully received your complaint.
                Tracking ID: {complaint.tracking_token}
                
                - UrbanWatch+ Team
                """
                
                try:
                    # CALLING SEND_ALERT
                    print("Calling send_alert function...")
                    send_alert(subject, message, [request.user.email])
                    print("send_alert called successfully.")
                except Exception as e:
                    print(f"CRITICAL ERROR CALLING EMAIL: {e}")
            else:
                print("❌ SKIPPING EMAIL: User has no email address in database.")

            # Inside submit_complaint view, after complaint.save()
            messages.success(request, f'Complaint Submitted! Your Tracking ID is: {complaint.tracking_token}')
            print("✅ Form is valid! Redirecting...")
            return redirect(f"{reverse('complaints:submit_success')}?token={complaint.tracking_token}")  #redirect to citizen's complaints page
        else:
            print("❌ Form Errors:", form.errors) # This will print to your terminal/console
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ComplaintForm() #initialize an empty form for GET request
    
    return render(request, 'complaints/submit_complaint.html', {'form': form, 'citizen': citizen})


@login_required
def my_complaints(request): 
    """View for the citizen to see their submitted complaints."""
    try:
        citizen = Citizen.objects.get(user=request.user)
        complaints = citizen.complaints.all() #fetch complaints related to this citizen
    except Citizen.DoesNotExist:
        complaints = []  # Fixed: initialize empty list
        messages.error(request, "Citizen profile not found.")

    context = {
        'complaints': complaints,
    }

    return render(request, 'complaints/my_complaints.html', context)

def track_issue(request):
    """Public view to track a complaint using a UUID token."""
    token = request.GET.get('token', '').strip()
    complaint = None
    timeline = []

    if token:
        try:
            # Search for the complaint using the UUID
            complaint = Complaint.objects.get(tracking_token=token)
            
            # Build the timeline (Same logic as dashboard)
            timeline = [
                {'label': 'Submitted', 'date': complaint.created_at, 'completed': True, 'desc': 'Complaint received.'},
                {'label': 'Assigned', 'date': complaint.assigned_at, 'completed': bool(complaint.assigned_at), 'desc': 'Officer assigned.'},
                {'label': 'In Progress', 'date': complaint.in_progress_at, 'completed': bool(complaint.in_progress_at), 'desc': 'Contractor working.'},
                {'label': 'Completed', 'date': complaint.completed_at, 'completed': bool(complaint.completed_at), 'desc': 'Work finished.'},
                {'label': 'Closed', 'date': complaint.closed_at, 'completed': bool(complaint.closed_at), 'desc': 'Verified & Closed.'},
            ]
        except (Complaint.DoesNotExist, ValueError):
            messages.error(request, "Invalid Tracking ID. Please check and try again.")

    return render(request, 'complaints/track_issue.html', {
        'complaint': complaint,
        'token': token,
        'timeline': timeline
    })