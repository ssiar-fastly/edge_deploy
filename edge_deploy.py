import os
import requests
import argparse
import time
import json  # Needed to parse the JSON response

# Constants
BASE_URL = "https://dashboard.signalsciences.net/api/v0"
MAX_RETRIES = 3
RETRY_WAIT = 10
PROV_RETRY_WAIT = 45

def get_headers(ngwaf_user_email, ngwaf_token, fastly_token=None):
    # Generate headers for API requests
    headers = {
        "Content-Type": "application/json", 
        "x-api-user": ngwaf_user_email, 
        "x-api-token": ngwaf_token
    }
    if fastly_token:
        headers["Fastly-Key"] = fastly_token
    return headers

def retry_api_call(func):
    # Decorator to retry API calls upon failure
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < MAX_RETRIES:
            response = func(*args, **kwargs)
            if response.status_code == 200:
                return response
            elif response.status_code == 401:
                print(f"API call failed with Unauthorized (401) error. No retry will be attempted.")
                return response
            retries += 1
            error_message = response.text if response.text else "No additional error message provided"
            print(f"API call failed, response code: {response.status_code}. Error details: {error_message}. Retrying in {RETRY_WAIT}s... (Retry {retries}/{MAX_RETRIES})")
            time.sleep(RETRY_WAIT)
        return response
    return wrapper

@retry_api_call
def check_and_create_site(ngwaf_user_email, ngwaf_token, corp_name, site_name):
    # Check if a site exists, and create it if it doesn't
    site_exists_url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}"
    check_response = requests.get(site_exists_url, headers=get_headers(ngwaf_user_email, ngwaf_token))
    if check_response.status_code == 200:
        print(f"Site {site_name} already exists.")
        return check_response  # Return response for consistency
    elif check_response.status_code == 400:
        try:
            response_json = check_response.json()
            if response_json.get("message") == "Site not found":
                print(f"Site {site_name} does not exist, creating...")
                create_site_url = f"{BASE_URL}/corps/{corp_name}/sites"
                # Ensure site_name meets the character requirement
                site_details = {
                    "name": site_name,
                    "displayName": site_name,  # Ensure displayName is correctly set
                    "agentLevel": "block",
                    "blockHTTPCode": 406,
                    "blockDurationSeconds": 86400,
                    "blockRedirectURL": ""
                }
                create_response = requests.post(create_site_url, headers=get_headers(ngwaf_user_email, ngwaf_token), json=site_details)
                if create_response.status_code in [200, 201]:
                    print(f"Site {site_name} created successfully.")
                    return create_response  # Return response for consistency
                else:
                    print(f"Failed to create site {site_name}. Status Code: {create_response.status_code} - Details: {create_response.text}")
                    return create_response  # Return response to handle failure correctly
            else:
                print(f"Unexpected error message received. Message: {response_json.get('message')}")
                return check_response  # Handle unexpected message correctly
        except json.JSONDecodeError:
            print("Failed to parse response as JSON.")
            return check_response  # Handle JSON parsing error
    else:
        print(f"Unexpected response while checking for site existence. Status Code: {check_response.status_code} - Details: {check_response.text}")
        return check_response  # Handle unexpected response status code

@retry_api_call
def create_edge_security_object(ngwaf_user_email, ngwaf_token, corp_name, site_name):
    # Create an edge security object for the specified corp and site
    print("Creating edge security object...")
    url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}/edgeDeployment"
    return requests.put(url, headers=get_headers(ngwaf_user_email, ngwaf_token))

@retry_api_call
def map_to_fastly_service(ngwaf_user_email, ngwaf_token, fastly_token, corp_name, site_name, fastly_sid, activate_version, percent_enabled):
    # Map the corp and site to a Fastly service and synchronize origins
    print(f"Waiting {PROV_RETRY_WAIT} seconds for edge configuration to complete...")
    time.sleep(PROV_RETRY_WAIT)
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

    if not check_and_create_site(args.ngwaf_user_email, args.ngwaf_token, args.corp_name, args.site_name):
        print("Exiting due to inability to ensure site existence.")
        exit()

    create_response = create_edge_security_object(args.ngwaf_user_email, args.ngwaf_token, args.corp_name, args.site_name)
    if create_response.status_code == 200:
        print("Edge security object created successfully.")
        map_response = map_to_fastly_service(args.ngwaf_user_email, args.ngwaf_token, args.fastly_token, args.corp_name, args.site_name, args.fastly_sid, args.activate, args.percent_enabled)
        if map_response.status_code == 200:
            print("Edge deployment completed successfully.")
        else:
            print(f"Edge deployment failed during mapping to Fastly service: Status Code {map_response.status_code} - Details: {map_response.text}")
    else:
        print(f"Failed to create edge security object. Status Code: {create_response.status_code} - Details: {create_response.text}")
