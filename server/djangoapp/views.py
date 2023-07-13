from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def get_about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def get_contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else: 
            context['message'] = "Invalid Username/Password Combination"
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['firstName']
        last_name = request.POST['lastName']
        email = request.POST['email']
        password = request.POST['password']
        user_exist = False
        try:
            User.objects.get(username = username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username = username, first_name = first_name,
            last_name = last_name, email = email, password = password)
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "User already exists. Please log in."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/ad3ea32e-d99c-4d84-ac0e-58b0030eb458/dealership-package/get-dealership"
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)
# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == 'GET':
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/ad3ea32e-d99c-4d84-ac0e-58b0030eb458/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        context["review_list"] = reviews
        context["dealer_id"] = dealer_id
    return render(request, 'djangoapp/dealer_details.html', context)
# Create a `add_review` view to submit a review
def add_review(request, dealer_id, **kwargs):
    if request.user.is_authenticated:
        if request.method == 'POST':
            review = {
                'time': datetime.utcnow().isoformat(),
                'dealership': dealer_id,
                'review': request.POST['review'],
                'purchase': request.POST['purchase'],
                'purchase_date': request.POST['purchase_date'],
                'car_make': request.POST['car_make'],
                'car_model': request.POST['car_model'],
                'car_year': request.POST['car_year']
            }
            
            json_payload = {'review' : review}
            url = "API_URL"
            headers = {'Content-Type': 'application/json'}
            response = post_request(url, json_payload, **kwargs)
            print(response.json())
            return render(request, 'djangoapp/dealer_details.html', {response : response})
        else:
            return redirect('djangoapp:index')
    else:
        return redirect('djangoapp:index')