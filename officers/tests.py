from django.test import TestCase
from django.contrib.auth.models import User
from users.models import Citizen
from officers.models import Officer
from contractors.models import Contractor
from complaints.models import Complaint

class OfficerAssignmentTest(TestCase):
    def setUp(self):
        # Create users
        self.officer_user = User.objects.create_user(username='officer1', password='Test@123', is_staff=True)
        self.citizen_user = User.objects.create_user(username='citizen1', password='Test@123')
        
        # Create citizen and officer
        self.citizen = Citizen.objects.create(user=self.citizen_user, name='Citizen One', region='north')
        self.officer = Officer.objects.create(user=self.officer_user, name='Officer One', region='north')
        
        # Create complaint
        self.complaint = Complaint.objects.create(
            title='Broken road',
            description='Multiple potholes',
            category='road',
            location='Main Street',
            region='north',
            citizen=self.citizen
        )
        
        # Login officer
        self.client.login(username='officer1', password='Test@123')
    
    def test_officer_dashboard_loads(self):
        response = self.client.get('/officers/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('unassigned_complaints', response.context)
    
    def test_assign_to_me(self):
        response = self.client.get(f'/officers/assign/{self.complaint.id}/')
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.officer, self.officer)
        self.assertEqual(self.complaint.status, 'assigned')
    
    def test_cannot_assign_different_region(self):
        # Create complaint in different region
        complaint2 = Complaint.objects.create(
            title='Issue in south',
            description='Test',
            category='other',
            location='South Street',
            region='south',
            citizen=self.citizen
        )
        response = self.client.get(f'/officers/assign/{complaint2.id}/')
        complaint2.refresh_from_db()
        self.assertIsNone(complaint2.officer)
    
    def test_status_update_with_validation(self):
        # First assign
        self.complaint.officer = self.officer
        self.complaint.status = 'assigned'
        self.complaint.save()
        
        # Try invalid transition
        response = self.client.post(f'/officers/complaint/{self.complaint.id}/update-status/', {
            'status': 'closed'  # Cannot go from assigned to closed
        })
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, 'assigned')  # Should not change
