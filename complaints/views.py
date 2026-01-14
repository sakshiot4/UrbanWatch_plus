from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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
           
            messages.success(request, 'Your complaint has been submitted successfully.')
            print("✅ Form is valid! Redirecting...")
            return redirect('complaints:submit_success')  #redirect to citizen's complaints page
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
