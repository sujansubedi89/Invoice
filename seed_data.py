from django.contrib.auth.models import User
from invoices.models import UserProfile

# Format: (username, first_name, last_name, role)
users_data = [
    ('jyaba',    'Jyaba',    'Admin',    'admin'),
    ('surendra', 'Surendra', 'Sir',      'manager'),
    ('tara',     'Tara',     'Sir',      'manager'),
    ('roshan',   'Roshan',   'Manager',  'manager'),
    ('sujan',    'Sujan',    'Employee', 'employee'),
]

for uname, fname, lname, role in users_data:
    u, created = User.objects.get_or_create(username=uname)
    u.first_name, u.last_name = fname, lname
    u.set_password('demo1234')
    u.save()
    
    p, _ = UserProfile.objects.get_or_create(user=u)
    p.role = role
    p.save()
    
    status = "Created" if created else "Updated"
    print(f"{status}: {uname} / demo1234 ({role})")
