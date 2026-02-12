import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.utils.crypto import get_random_string

# --- IMPORTS BASED ON YOUR MODELS ---
from officers.models import Officer
from contractors.models import Contractor
from complaints.models import Complaint

# Try importing Citizen from 'users' (as seen in your Complaint model import)
# If that fails, try 'citizens' app.
try:
    from users.models import Citizen
except ImportError:
    try:
        from citizens.models import Citizen
    except ImportError:
        # Final fallback if models are structured differently
        from core.models import Citizen

fake = Faker()

# Options based on your model choices
REGIONS = ['north', 'south', 'east', 'west', 'central']
CATEGORIES = ['water', 'road', 'electricity', 'sanitation', 'other']

class Command(BaseCommand):
    help = 'Populates the database with dummy data matching your specific Schema'

    def handle(self, *args, **kwargs):
        # Generate a unique Batch ID (e.g., "a1b2") to prevent username clashes
        batch_id = get_random_string(4).lower()
        self.stdout.write(f"Starting Batch Population: {batch_id}")

        try:
            with transaction.atomic():
                
                # =============================================
                # 1. CREATE OFFICERS (One per region)
                # =============================================
                new_officers = {}
                for region in REGIONS:
                    username = f"off_{region}_{batch_id}"
                    email = f"{username}@urban.com"
                    
                    user = User.objects.create_user(username=username, email=email, password="password123")
                    
                    officer = Officer.objects.create(
                        user=user,
                        name=f"Officer {region.capitalize()} ({batch_id})",
                        region=region,
                        # Phone must be string, allow flexible for officer as validation wasn't strict in snippet
                        phone=fake.numerify("##########"),
                        email=email
                    )
                    new_officers[region] = officer
                    self.stdout.write(f" - Created {username}")

                # =============================================
                # 2. CREATE CONTRACTORS
                # =============================================
                new_contractors = []
                
                # A. Approved Contractors (Active)
                for region in REGIONS:
                    for cat in CATEGORIES:
                        username = f"cont_{region}_{cat}_{batch_id}"[:30]
                        email = f"{username}@build.com"
                        
                        user = User.objects.create_user(username=username, email=email, password="password123")
                        
                        # Find the officer for this region to "approve" them
                        approving_officer = new_officers.get(region)

                        cont = Contractor.objects.create(
                            user=user,
                            name=f"{fake.first_name()} ({batch_id})",
                            company_name=f"{fake.company()} {cat.capitalize()} {batch_id}",
                            region=region,
                            specialization=cat,
                            status='approved',
                            phone=fake.numerify("##########"), # Strictly 10 digits
                            email=email,
                            license_number=f"LIC-{batch_id}-{random.randint(1000,9999)}",
                            approved_by=approving_officer,
                            approved_at=timezone.now()
                        )
                        new_contractors.append(cont)

                # B. Pending Contractors (For Approval Demo)
                for i in range(2):
                    username = f"pending_{i}_{batch_id}"
                    user = User.objects.create_user(username=username, password="password123")
                    
                    # Create the Contractor profile linked to the User
                    Contractor.objects.create(
                        user=user,
                        name=fake.name(),
                        company_name=f"New Applicant {fake.company()} {batch_id}",
                        region=random.choice(REGIONS),
                        specialization=random.choice(CATEGORIES),
                        status='pending',
                        phone=fake.numerify("##########"), # Strictly 10 digits
                        email=fake.email(),
                        license_number=f"TEMP-{batch_id}-{i}"
                    )

                # =============================================
                # 3. CREATE CITIZENS
                # =============================================
                new_citizens = []
                for i in range(4):
                    username = f"citizen_{i}_{batch_id}"
                    user = User.objects.create_user(username=username, password="password123")
                    
                    cit = Citizen.objects.create(
                        user=user,
                        name=f"{fake.name()} ({batch_id})",
                        phone=fake.numerify("##########"), # Strictly 10 digits
                        address=fake.address(),
                        region=random.choice(REGIONS),
                        is_registered=True
                    )
                    new_citizens.append(cit)

                # =============================================
                # 4. CREATE COMPLAINTS (SCENARIOS)
                # =============================================
                self.stdout.write("Generating Scenarios...")

                # --- Scenario A: Reported / Unassigned ---
                Complaint.objects.create(
                    title=f"Open Manhole ({batch_id})",
                    description="Dangerous open manhole in the middle of the street.",
                    citizen=new_citizens[0],
                    region='central',
                    category='sanitation',
                    location="Central Ave, Block B",
                    status='reported', # Default status per your model
                    created_at=timezone.now()
                )

                # --- Scenario B: Assigned ---
                # Find a contractor matching region & category
                target_cont = next((c for c in new_contractors if c.region == 'north' and c.specialization == 'electricity'), None)
                
                if target_cont:
                    Complaint.objects.create(
                        title=f"Streetlight Outage ({batch_id})",
                        description="Whole street is dark.",
                        citizen=new_citizens[1],
                        region='north',
                        category='electricity',
                        location="Sector 7",
                        status='assigned',
                        officer=new_officers['north'],
                        contractor=target_cont,
                        assigned_at=timezone.now(),
                        created_at=timezone.now()
                    )

                # --- Scenario C: REJECTED (Lives in 'in_progress' with feedback) ---
                target_cont_rej = next((c for c in new_contractors if c.region == 'central' and c.specialization == 'road'), None)
                
                if target_cont_rej:
                    Complaint.objects.create(
                        title=f"Bad Pothole Fix ({batch_id})",
                        description="Pothole reappeared after rain.",
                        citizen=new_citizens[0],
                        region='central',
                        category='road',
                        location="Main Market",
                        status='in_progress', 
                        officer=new_officers['central'],
                        contractor=target_cont_rej,
                        assigned_at=timezone.now(),
                        in_progress_at=timezone.now(),
                        created_at=timezone.now(),
                        # Triggers the 'Rejected' tab
                        officer_feedback="Material washed away immediately. Please redo with concrete mix." 
                    )

                # --- Scenario D: Completed ---
                target_cont_comp = next((c for c in new_contractors if c.region == 'east' and c.specialization == 'water'), None)
                if target_cont_comp:
                    Complaint.objects.create(
                        title=f"Pipeline Leak ({batch_id})",
                        description="Fixed the leakage near the mall.",
                        citizen=new_citizens[2],
                        region='east',
                        category='water',
                        location="East Side Mall",
                        status='completed',
                        officer=new_officers['east'],
                        contractor=target_cont_comp,
                        assigned_at=timezone.now(),
                        in_progress_at=timezone.now(),
                        completed_at=timezone.now(),
                        created_at=timezone.now(),
                        # Note: Validation requires completion_image for 'completed', 
                        # but in script/shell we can bypass clean() unless we call full_clean().
                        # For demo UI to work, you might want to manually upload an image later.
                    )

            self.stdout.write(self.style.SUCCESS(f'Successfully added batch {batch_id}!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))