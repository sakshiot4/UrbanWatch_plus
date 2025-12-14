"""
Global authentication adapter for allauth.
Handles post-login redirect for all user roles:
- Citizens → /users/dashboard/
- Officers → /officers/dashboard/
- Contractors → /contractors/dashboard/
"""
from django.shortcuts import resolve_url
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages


class CustomAccountAdapter(DefaultAccountAdapter):
    """Controls where users go after login based on role & status."""
    
    def get_login_redirect_url(self, request):
        user = request.user
        
        # Officer
        if hasattr(user, 'officer_profile'):
            return resolve_url('officers:dashboard')
        
        # Contractor
        if hasattr(user, 'contractor_profile'):
            contractor = user.contractor_profile

            #check status.
            if contractor.status == 'pending':
                return resolve_url('contractors:pending_approval')
            
            if contractor.status == 'rejected':
                return resolve_url('contractors:application_rejected')
            
            #if approved.
            return resolve_url('contractors:contractor_dashboard')
        
        # Default: Citizen login.
        return resolve_url('users:citizen_dashboard')
