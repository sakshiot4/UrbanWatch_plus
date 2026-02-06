from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import ContractorSignupForm

@require_http_methods(["GET", "POST"])
def contractor_signup(request):
    """Contractor signup page."""

    # 1. Improved Redirect Logic
    if request.user.is_authenticated:
        # Check if they are a contractor
        if hasattr(request.user, 'contractor_profile'):
            return redirect('contractors:contractor_dashboard')
        # If they are just a normal user/citizen, send them to their specific dashboard
        # Avoid redirecting to a page that might loop back here
        return redirect('users:citizen_dashboard') 

    if request.method == 'POST':
        form = ContractorSignupForm(request.POST)
        
        # 2. Check if the form is valid
        if form.is_valid():
            # Ensure this matches the method name in your forms.py (save vs try_save)
            user = form.save(request) 
            
            messages.success(request, "Account created! Please login. Approval is pending.")
            return redirect('account_login')
        
        # NOTE: Removed the 'messages.error' loop. 
        # The 'form' object already carries the errors to the template.
        
    else:
        form = ContractorSignupForm()

    return render(request, 'account/contractor_signup.html', {'form': form})