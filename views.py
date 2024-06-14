# admin/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import User
from .forms import EmployeeForm
from .forms import *
from .models import Employee
from .forms import ForgotPasswordForm
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned, ValidationError
from django.contrib.auth.hashers import make_password
from .models import ViolationRecord
from django.conf import settings
import os
import re
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate,login as auth_login
# import cv2


def is_valid_username(username):
    # Check if username is a valid email address
    if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', username):
        return True
    # Check if username is a valid 11-digit phone number
    elif re.match(r'^\d{11}$', username):
        return True
    else:
        return False

from django.contrib.auth.hashers import make_password

from django.contrib import messages

from django.contrib import messages

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        # Check if password and confirm password match
        if password != confirm_password:
            return render(request, 'admin/register.html', {'error': 'Passwords do not match'})
        
        # Check if password meets minimum length requirement
        if len(password) < 8:
            return render(request, 'admin/register.html', {'error': 'Password must be at least 8 characters long'})
        
        if not is_valid_username(username):
            return render(request, 'admin/register.html', {'error': 'Invalid username. Please enter a valid email.'})
        elif User.objects.filter(username=username).exists():
            return render(request, 'admin/register.html', {'error': 'Username already exists. Please choose a different username.'})
        else:
            # Hash the password
            hashed_password = make_password(password)
            # Create user with hashed password
            User.objects.create(username=username, password=hashed_password)
            # Redirect to the login page
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    return render(request, 'admin/register.html')




'''
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Check if username and password match
        if User.objects.filter(username=username, password=password).exists():
            return redirect('dashboard')  # Redirect to dashboard upon successful login
        else:
            # Handle invalid credentials
            return render(request, 'admin/login.html', {'error': 'Invalid credentials'})
    return render(request, 'admin/login.html')
'''

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # User authentication successful, log in the user
            auth_login(request, user)
            return redirect('dashboard')  # Redirect to dashboard upon successful login
        else:
            # Handle invalid credentials
            return render(request, 'admin/login.html', {'error': 'Invalid credentials'})
    return render(request, 'admin/login.html')

# admin/views.py

def dashboard(request):
    employees = Employee.objects.all()
    recent_violations = ViolationRecord.objects.order_by('-timestamp')[:5]
    return render(request, 'admin/dashboard.html', {'employees': employees, 'recent_violations': recent_violations})


from django.core.exceptions import ValidationError
from .forms import EmployeeForm

def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            try:
                form.clean_unique_cnic()  # Check uniqueness of CNIC
                form.clean_valid_dob_email()  # Check format of DOB and email
            except ValidationError as e:
                form.add_error(None, e)  # Add validation error to form
            else:
                form.save()  # Save the form data if valid
                messages.success(request, 'Employee added successfully.')
                return redirect('dashboard')
        else:
            # If form is invalid, return to the form page with error messages
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeForm()
    return render(request, 'admin/add_employee.html', {'form': form})

# admin/views.py

def view_employee(request, employee_id):
    employee = Employee.objects.get(pk=employee_id)
    return render(request, 'admin/view_employee.html', {'employee': employee})

# admin/views.py

def update_employee(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('view_employee', employee_id=employee_id)
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'admin/update_employee.html', {'form': form, 'employee_id': employee_id})


def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    if request.method == 'POST':
        employee.delete()
        return redirect('dashboard')
    return render(request, 'admin/delete_employee.html', {'employee': employee})

def search_employee(request):
    query = request.GET.get('q')
    employees = Employee.objects.filter(name__icontains=query)
    return render(request, 'admin/dashboard.html', {'employees': employees, 'query': query})


from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from django.contrib import messages

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            
            # Check if password meets minimum length requirement
            if len(new_password) < 8:
                return render(request, 'admin/forgot_password.html', {'form': form, 'error': 'Password must be at least 8 characters long'})
            
            if new_password == confirm_password:
                # Filter users by username
                users = User.objects.filter(username=username)
                if users.exists():
                    if users.count() == 1:
                        user = users.first()
                        # Hash the new password
                        hashed_password = make_password(new_password)
                        # Update the user's password
                        user.set_password(new_password)
                        user.save()
                        messages.success(request, 'Password reset successful. Please log in with your new password.')
                        return redirect('login')  # Redirect to login page after resetting password
                    else:
                        return render(request, 'admin/forgot_password.html', {'form': form, 'error': 'Multiple users found with this username. Please contact support.'})
                else:
                    return render(request, 'admin/forgot_password.html', {'form': form, 'error': 'User does not exist'})
            else:
                return render(request, 'admin/forgot_password.html', {'form': form, 'error': 'Passwords do not match'})
    else:
        form = ForgotPasswordForm()
    return render(request, 'admin/forgot_password.html', {'form': form})



'''
def live_stream(request):
    # Add logic to retrieve live streams from cameras
    # For now, let's assume a list of dummy camera URLs
    camera_urls = [
        "https://example.com/camera1_stream",
        "https://example.com/camera2_stream",
        "https://example.com/camera3_stream",
        "https://example.com/camera4_stream",
        "https://example.com/camera5_stream",
        "https://example.com/camera6_stream",
        "https://example.com/camera7_stream",
        "https://example.com/camera8_stream",
        "https://example.com/camera9_stream",
        "https://example.com/camera10_stream",
    ]
    return render(request, 'admin/live_stream.html', {'camera_urls': camera_urls})
'''


def live_stream(request):
    # Define the directory where your MP4 videos are stored
    mp4_video_dir = os.path.join(settings.MEDIA_ROOT, 'videos')

    # Get a list of all MP4 files in the directory
    mp4_video_files = [file for file in os.listdir(mp4_video_dir) if file.endswith('.mp4')]

    # Construct URLs for the MP4 videos
    mp4_video_urls = [os.path.join(settings.MEDIA_URL, 'videos', file) for file in mp4_video_files]

    return render(request, 'admin/live_stream.html', {'mp4_video_urls': mp4_video_urls})


def violation_records(request):
    all_violations = ViolationRecord.objects.order_by('-timestamp')  # Order violations by timestamp in descending order
    return render(request, 'admin/violation_records.html', {'all_violations': all_violations})


def delete_violation(request, violation_id):
    violation = get_object_or_404(ViolationRecord, id=violation_id)
    if request.method == 'POST':
        violation.delete()
        return redirect('violation_records')
    return render(request, 'admin/violation_records.html', {'latest_violations': ViolationRecord.objects.order_by('-timestamp')[:10]})

# In your views.py

from django.db.models import Q

def list_employees(request):
    # Retrieve all employees
    employees = Employee.objects.all()
    
    # Filter employees based on search query
    query = request.GET.get('q')
    if query:
        # Filter employees by name or CNIC containing the query
        employees = employees.filter(Q(name__icontains=query) | Q(cnic__icontains=query))
    
    # Check if the search query is empty
    is_empty_query = not query
    
    return render(request, 'admin/list_employees.html', {'employees': employees, 'query': query, 'is_empty_query': is_empty_query})

# views.py
from .forms import VehicleForm

def add_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle added successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VehicleForm()
    return render(request, 'admin/add_vehicle.html', {'form': form})



from .models import Vehicle

from django.db.models import Q

def list_vehicles(request):
    # Retrieve all vehicles
    vehicles = Vehicle.objects.all()
    
    # Filter vehicles based on search query
    query = request.GET.get('q')
    if query:
        # Split the query into individual parts
        query_parts = query.split()
        # Create a Q object to filter vehicles by matching any part of the plate number or make/model/year
        filter_condition = Q()
        for part in query_parts:
            filter_condition |= Q(plate_number__icontains=part) | \
                                Q(make__icontains=part) | \
                                Q(model__icontains=part) | \
                                Q(year__icontains=part)
        # Filter the vehicles
        vehicles = vehicles.filter(filter_condition)
    
    return render(request, 'admin/list_vehicles.html', {'vehicles': vehicles, 'query': query})

# admin/views.py

from django.shortcuts import render, get_object_or_404
from .models import Vehicle

def view_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    return render(request, 'admin/view_vehicle.html', {'vehicle': vehicle})

from django.shortcuts import render, redirect, get_object_or_404
from .forms import VehicleForm
from .models import Vehicle

def update_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            # Update the vehicle instance with the form data
            vehicle.make = form.cleaned_data['make']
            vehicle.model = form.cleaned_data['model']
            vehicle.plate_number = form.cleaned_data['plate_number']
            vehicle.year = form.cleaned_data['year']
            vehicle.save()
            return redirect('view_vehicle', vehicle_id=vehicle_id)
    else:
        # Populate the form with the current instance data
        form = VehicleForm(initial={
            'make': vehicle.make,
            'model': vehicle.model,
            'plate_number': vehicle.plate_number,
            'year': vehicle.year,
        })
    return render(request, 'admin/update_vehicle.html', {'form': form, 'vehicle_id': vehicle_id})

def delete_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    if request.method == 'POST':
        vehicle.delete()
        return redirect('dashboard')
    return render(request, 'admin/delete_vehicle.html', {'vehicle': vehicle})


import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import LicensePlate, Vehicle

def import_csv(request):
    imported_data = []
    authorized_data = []
    unauthorized_data = []

    # Retrieve all plate numbers from the list of vehicles
    vehicle_plate_numbers = set(Vehicle.objects.values_list('plate_number', flat=True))
    
    with open('admin/automatic-number-plate-recognition-python-yolov8-main/test.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            license_number = row['license_number']
            instance = LicensePlate.objects.create(
                frame_nmr=row['frame_nmr'],
                car_id=row['car_id'],
                car_bbox=row['car_bbox'],
                license_plate_bbox=row['license_plate_bbox'],
                license_plate_bbox_score=row['license_plate_bbox_score'],
                license_number=license_number,
                license_number_score=row['license_number_score']
            )
            imported_data.append(instance)
            
            # Check if the license number exists in the list of vehicles
            if license_number in vehicle_plate_numbers:
                authorized_data.append(instance)
            else:
                unauthorized_data.append(instance)

    # Set up pagination for imported_data
    paginator = Paginator(imported_data, 20)  # Show 20 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    messages.success(request, 'CSV data imported successfully.')
    return render(request, 'admin/import_done.html', {
        'page_obj': page_obj,
        'authorized_data': authorized_data,
        'unauthorized_data': unauthorized_data
    })




# admin/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Employee, ViolationRecord, Vehicle, LicensePlate
from .forms import EmployeeForm, ForgotPasswordForm, VehicleForm
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
import os
import re

def dashboard(request):
    employees = Employee.objects.all()[:5]  # Display first 5 employees
    recent_violations = ViolationRecord.objects.order_by('-timestamp')[:5]  # Display recent 5 violations
    vehicles = Vehicle.objects.all()[:5]  # Display first 5 vehicles
    latest_license_plates = LicensePlate.objects.order_by('-id')[:5]  # Display recent 5 license plates
    
    # Define the directory where your MP4 videos are stored
    mp4_video_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
    # Get a list of all MP4 files in the directory
    mp4_video_files = [file for file in os.listdir(mp4_video_dir) if file.endswith('.mp4')]
    # Construct URLs for the MP4 videos
    mp4_video_urls = [os.path.join(settings.MEDIA_URL, 'videos', file) for file in mp4_video_files]

    context = {
        'employees': employees,
        'recent_violations': recent_violations,
        'vehicles': vehicles,
        'latest_license_plates': latest_license_plates,
        'mp4_video_urls': mp4_video_urls[:5],  # Display first 5 videos
    }
    
    return render(request, 'admin/dashboard.html', context)
