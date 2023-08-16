from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarDealer, DealerReview, CarMake, CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request,get_dealer_by_id_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import uuid

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
    if request.method == "GET":
        context = {}
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/28d0b867-6bcc-4fb3-a6e3-9623b43f327e/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealerships']=dealerships
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        # return HttpResponse(dealer_names)
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context={}
        url1 = "https://eu-de.functions.appdomain.cloud/api/v1/web/28d0b867-6bcc-4fb3-a6e3-9623b43f327e/dealership-package/get-review"
        url2 = "https://eu-de.functions.appdomain.cloud/api/v1/web/28d0b867-6bcc-4fb3-a6e3-9623b43f327e/dealership-package/get-dealership"
        # Get dealers reviews from the URL
        reviews = get_dealer_reviews_from_cf(url1,dealer_id)
        dealer = get_dealer_by_id_from_cf(url2, dealer_id)
        context['reviews']=reviews
        context['dealer']=dealer
        # review_text = ' '.join([review.sentiment for review in reviews])
        # Return a list of dealer short name
        # return HttpResponse(review_text)
        return render(request, 'djangoapp/dealer_details.html', context)



# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == "GET":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/28d0b867-6bcc-4fb3-a6e3-9623b43f327e/dealership-package/get-dealership"
        dealer = get_dealer_by_id_from_cf(url, dealer_id)
        context = {
            "cars": CarModel.objects.all(),
            "dealer": dealer
        }
        return render(request, 'djangoapp/add_review.html', context)
    if request.method == "POST":
            form = request.POST
            review = dict()
            unique_id = uuid.uuid4()
            review["name"] = request.user.username
            review["id"] = int.from_bytes(unique_id.bytes, byteorder='big')
            review["dealership"] = dealer_id
            review["review"] = form["content"]
            review["purchase"] = form.get("purchasecheck")
            review["another"] = "field"
            if review["purchase"]:
                review["purchase_date"] = str(datetime.strptime(form.get("purchasedate"), "%Y-%m-%d"))
            car = CarModel.objects.get(pk=form["car"])
            review["car_make"] = car.car_make.name
            review["car_model"] = car.name
            review["car_year"] = car.year.strftime("%Y")
            # If the user bought the car, get the purchase date
            if form.get("purchasecheck"):
                review["purchase_date"] = str(datetime.strptime(form.get("purchasedate"), "%Y-%m-%d"))
            else: 
                review["purchase_date"] = None
            url = "https://eu-de.functions.appdomain.cloud/api/v1/web/28d0b867-6bcc-4fb3-a6e3-9623b43f327e/dealership-package/post-review" 
            
            json_payload = {"review": review}
            result = post_request(url, json_payload, dealerId=dealer_id)
            if (result):
                return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
            else:
            # After posting the review the user is redirected back to the dealer details
                 return redirect("djangoapp:dealer_details", dealer_id=dealer_id)


