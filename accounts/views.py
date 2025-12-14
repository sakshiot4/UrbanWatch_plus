from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.views.decorators.http import require_http_methods

from .forms import ContractorSignupForm

@require_http_methods(["GET", "POST"])
def contractor_signup(request):
    """Contractor signup page."""

    #If loggged in, redirect away.
    if request.user.is_authenticated:
        if hasattr(request.user, 'contractor_profile'):
            return redirect('contractors:contractor_dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = ContractorSignupForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            messages.success(request, "Account created! Please wait for officer approval.")

            return redirect('account_login')
        else:
            #Show form errors.
            for field, errors in form.errors.items():
                messages.error(request, f"{field}: {errors}")

    else:
        form = ContractorSignupForm()

    return render(request, 'account/contractor_signup.html',
                  {'form': form})

