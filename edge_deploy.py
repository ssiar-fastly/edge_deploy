import os
import requests
import argparse
import time

# Constants
BASE_URL = "https://dashboard.signalsciences.net/api/v0"
MAX_RETRIES = 3
RETRY_WAIT = 10

def get_headers(ngwaf_user_email, ngwaf_token, fastly_token=None):
    # Generate headers for API requests
    headers = {
        "Content-Type": "application/json", 
        "x-api-user": ngwaf_user_email, 
        "x-api-token": ngwaf_token
    }
    if fastly_token:
        headers["Fastly-Token"] = fastly_token
    return headers

def retry_api_call(func):
    # Decorator to retry API calls upon failure
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < MAX_RETRIES:
            response = func(*args, **kwargs)
            if response.status_code == 200:
                return response
            retries += 1
            error_message = response.text if response.text else "No additional error message provided"
            print(f"API call failed, response code: {response.status_code}. Error details: {error_message}. Retrying in {RETRY_WAIT}s... (Retry {retries}/{MAX_RETRIES})")
            time.sleep(RETRY_WAIT)
        return response
    return wrapper

@retry_api_call
def create_edge_security_object(ngwaf_user_email, ngwaf_token, corp_name, site_name):
    # Create an edge security object for the specified corp and site
    print("Creating edge security object...")
    url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}/edgeDeployment"
    return requests.put(url, headers=get_headers(ngwaf_user_email, ngwaf_token))

@retry_api_call
def map_to_fastly_service(ngwaf_user_email, ngwaf_token, fastly_token, corp_name, site_name, fastly_sid, activate_version, percent_enabled):
    # Map the corp and site to a Fastly service and synchronize origins
    print("Waiting 60 seconds for edge configuration to complete...")
    time.sleep(60)
    print("Mapping to Fastly service...")
    url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}/edgeDeployment/{fastly_sid}"
    payload = {"activateVersion": activate_version, "percentEnabled": percent_enabled}
    return requests.put(url, headers=get_headers(ngwaf_user_email, ngwaf_token, fastly_token), json=payload)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy NG WAF on Fastly Services")
    parser.add_argument('--ngwaf_user_email', default=os.environ.get('NGWAF_USER_EMAIL'), help='NGWAF user email')
    parser.add_argument('--ngwaf_token', default=os.environ.get('NGWAF_TOKEN'), help='NGWAF API token')
    parser.add_argument('--fastly_token', default=os.environ.get('FASTLY_TOKEN'), help='Fastly API token')
    parser.add_argument('--corp_name', default=os.environ.get('CORP_NAME'), help='Corporation name')
    parser.add_argument('--site_name', default=os.environ.get('SITE_NAME'), help='Site name')
    parser.add_argument('--fastly_sid', default=os.environ.get('FASTLY_SID'), help='Fastly Service ID')
    parser.add_argument('--activate', type=lambda x: (str(x).lower() == 'true'), default=os.environ.get('ACTIVATE', 'false').lower() == 'true', help='Activate the Fastly service version')
    parser.add_argument('--percent_enabled', type=int, default=int(os.environ.get('PERCENT_ENABLED', 0)), help='Percentage of traffic to send to NG WAF')

    args = parser.parse_args()

    create_response = create_edge_security_object(args.ngwaf_user_email, args.ngwaf_token, args.corp_name, args.site_name)
    if create_response.status_code == 200:
        print("Edge security object created successfully.")
        map_response = map_to_fastly_service(args.ngwaf_user_email, args.ngwaf_token, args.fastly_token, args.corp_name, args.site_name, args.fastly_sid, args.activate, args.percent_enabled)
        if map_response.status_code == 200:
            print("Edge deployment completed successfully.")
        else:
            print(f"Edge deployment failed during mapping to Fastly service: Status Code {map_response.status_code} - Details: {map_response.text}")
    else:
        print("Failed to create edge security object.")
