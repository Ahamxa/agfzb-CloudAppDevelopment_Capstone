import requests
import json
# import related models here
from requests.auth import HTTPBasicAuth
from .models import CarDealer, DealerReview
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 \
    import Features, SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)

def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print(json_payload)
    print("GET from {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
    
        # For each dealer object
        for dealer in json_result:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
            id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
            short_name=dealer_doc["short_name"],
            st=dealer_doc["st"], zip=dealer_doc["zip"],state=dealer_doc["state"])
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list

def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url,dealerId=dealerId)
    if json_result:
        # For each dealer object
        for review_doc in json_result:
            dealerReview_obj = DealerReview(
                dealership=review_doc["dealership"], 
                name=review_doc["name"], 
                purchase=review_doc["purchase"],
                review=review_doc["review"], 
                purchase_date=review_doc["purchase_date"], 
                car_make=review_doc["car_make"], 
                car_model=review_doc["car_model"],
                car_year=review_doc["car_year"], 
                sentiment="NULL", 
                id=review_doc["id"])

            dealerReview_obj.sentiment = analyze_review_sentiments(dealerReview_obj.review)
            results.append(dealerReview_obj)

    return results




def get_dealer_by_id_from_cf(url, dealerId):
    # Call get_request with a URL parameter
    json_result = get_request(url,dealerId=dealerId)
    if json_result:
        # For each dealer object
        for dealer_doc in json_result:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
            id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
            short_name=dealer_doc["short_name"],
            st=dealer_doc["st"], zip=dealer_doc["zip"],state=dealer_doc["state"])

    return dealer_obj

def get_dealer_by_state_from_cf(url, state):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url,state=state)
    if json_result:
        # For each dealer object
        for dealer in json_result:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
            id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
            short_name=dealer_doc["short_name"],
            st=dealer_doc["st"], zip=dealer_doc["zip"],state=dealer_doc["state"])
            results.append(dealer_obj)

    return results



# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    api_key="dmzKWQLGt5tfvp8I0Ag2OKrsdHe2rHT8OPF-uE1efVPF"
    url="https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/a873f678-deb0-4363-a870-3106f1ac8faf"
    authenticator = IAMAuthenticator(api_key) 

    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator) 

    natural_language_understanding.set_service_url(url) 

    response = natural_language_understanding.analyze( text=text+"hello hello hello",features=Features(sentiment=SentimentOptions(targets=[text+"hello hello hello"]))).get_result() 

    label=json.dumps(response, indent=2) 

    label = response['sentiment']['document']['label'] 

    return(label) 




