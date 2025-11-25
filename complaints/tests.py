from django.test import TestCase
from django.contrib.auth.models import User
from users.models import Citizen
from .models import Complaint
from django.urls import reverse

# Create your tests here.
class ComplaintModelTest(TestCase):
    def setUp(self):
        #create a user and citizen profile.
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.citizen = Citizen.objects.create(user=self.user, address='123 Main St', phone_number='1234567890')

        def test_create_complaint(self):
            complaint = Complaint.objects.create(
                title='Water Leakage issue',
                description='There is a major water leakage in my area.',
                category='water',
                location='123 Main St',
                region='Downtown',
                citizen = self.citizen,
            )

            self.assertEqual(Complaint.objects.count(), 1) #check one complaint created.
            self.assertEqual(complaint.status, 'reported') #check default status
            self.assertEqual(complaint.citizen, self.citizen) #check citizen association
            self.assertEqual(complaint.title, 'Water Leakage issue')
            self.assertEqual(complaint.category, 'water')
            self.assertEqual(complaint.citizen.name, 'testuser')

class ComplaintViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='citizen2', password='Test@123')
        self.citizen = Citizen.objects.create(user=self.user, name='Citizen Two')
        self.client.login(username='citizen2', password='Test@123')

    def test_submit_complaint_view(self):
        url = reverse('complaints:submit_complaint')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, {
            'title': 'Broken road',
            'description': 'Several potholes causing risk',
            'category': 'road',
            'location': 'Main Avenue'
            # Add any additional required fields
        })
        # Handle redirect after success
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Complaint.objects.count(), 1)
        complaint = Complaint.objects.first()
        self.assertEqual(complaint.title, 'Broken road')
        self.assertEqual(complaint.citizen, self.citizen)
