from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarDealer, DealerReview, CarMake, CarModel
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
def about(request):
    return render(request, 'djangoapp/about.html')




# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/login.html', context)
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)


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
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    # context = {}
    # if request.method == "GET":
    #     return render(request, 'djangoapp/index.html', context)
    if request.method == "GET":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/28d0b867-6bcc-4fb3-a6e3-9623b43f327e/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/28d0b867-6bcc-4fb3-a6e3-9623b43f327e/dealership-package/get-review"
        # Get dealers reviews from the URL
        reviews = get_dealer_reviews_from_cf(url,dealer_id)
        review_text = ' '.join([review.sentiment for review in reviews])
        # Return a list of dealer short name
        return HttpResponse(review_text)



# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    url = "https://eu-de.functions.appdomain.cloud/api/v1/web/28d0b867-6bcc-4fb3-a6e3-9623b43f327e/dealership-package/post-review"
    json_payload = {
    "review": 
    {
        "id": 1117,
        "name": request.user.username,
        "dealership": dealer_id,
        "review": request.POST['content'],
        "purchase": False,
        "another": "field",
         'purchase': bool(request.POST.get('purchase',False)),
            'car_make': car.car_make.name,
            'car_model': car.name,
            'car_year': car.year.strftime("%Y"),
            'purchase_date': datetime.strptime(request.POST['purchasedate'], "%m/%d/%Y").isoformat()
    }

    }
    if User.is_authenticated:
        response=post_request(url, json_payload, dealerId=dealer_id)
        return HttpResponse(response)
    else:
        return HttpResponse("no response")

