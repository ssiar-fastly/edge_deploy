import os
import requests
import argparse
import time

# Constants for the API endpoints
BASE_URL = "https://dashboard.signalsciences.net/api/v0"

# Function to get headers for making API calls
def get_headers(api_user, api_token, fastly_key=None):
    headers = {
        "Content-Type": "application/json",
        "x-api-user": api_user,
        "x-api-token": api_token
    }
    if fastly_key:
        headers["Fastly-Key"] = fastly_key
    return headers

# Function to create an edge security service
def create_edge_security_service(api_user, api_token, corp_name, site_name):
    url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}/edgeDeployment"
    response = requests.put(url, headers=get_headers(api_user, api_token))
    if response.status_code == 200:
        print("Edge security service created successfully.")
    else:
        print(f"Failed to create edge security service: {response.text}")
    return response.status_code == 200

# Function to confirm the creation of Compute instance resources
def confirm_compute_instance(api_user, api_token, corp_name, site_name):
    url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}/edgeDeployment"
    response = requests.get(url, headers=get_headers(api_user, api_token))
    if response.status_code == 200 and "ServicesAttached" in response.json():
        print("Compute instance resources confirmed.")
        return True
    else:
        print(f"Failed to confirm Compute instance resources: {response.text}")
    return False

# Function to map to the Fastly service with delay for edge configuration completion
def map_to_fastly_service(api_user, api_token, fastly_key, corp_name, site_name, fastly_sid, activate_version, percent_enabled):
    print("Waiting 60 seconds for edge configuration to complete...")
    time.sleep(60)  # Wait for 60 seconds

    url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}/edgeDeployment/{fastly_sid}"
    payload = {
        "activateVersion": activate_version,
        "percentEnabled": percent_enabled
    }
    response = requests.put(url, headers=get_headers(api_user, api_token, fastly_key), json=payload)
    
    if response.status_code == 200:
        print("Mapped to Fastly service successfully.")
    else:
        print(f"Failed to map to Fastly service: {response.text}")
        if response.status_code == 400 and "not yet complete" in response.text:
            print("The edge configuration is still in progress, trying again after 10 seconds.")
            time.sleep(10)
            response = requests.put(url, headers=get_headers(api_user, api_token, fastly_key), json=payload)
            if response.status_code == 200:
                print("Mapped to Fastly service successfully after waiting.")
            else:
                print(f"Failed to map to Fastly service after waiting: {response.text}")
    return response.status_code == 200

# Main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy NG WAF on Magento Fastly Services")
    parser.add_argument('--api_user', help='Email associated with the API user')
    parser.add_argument('--api_token', help='API token for Signal Sciences')
    parser.add_argument('--fastly_key', help='Fastly API key with write access')
    parser.add_argument('--corp_name', help='Name of the corporation')
    parser.add_argument('--site_name', help='Name of the site')
    parser.add_argument('--fastly_sid', help='Fastly Service ID to map')
    parser.add_argument('--activate', default=False, action='store_true', help='Whether to activate the Fastly service version')
    parser.add_argument('--percent_enabled', type=int, choices=range(0, 101), metavar="[0-100]", help='Percentage of traffic to send to the Next-Gen WAF', default=0)

    args = parser.parse_args()

    api_user = args.api_user or os.environ.get('API_USER')
    api_token = args.api_token or os.environ.get('API_TOKEN')
    fastly_key = args.fastly_key or os.environ.get('FASTLY_KEY')
    corp_name = args.corp_name or os.environ.get('CORP_NAME')
    site_name = args.site_name or os.environ.get('SITE_NAME')
    fastly_sid = args.fastly_sid or os.environ.get('FASTLY_SID')
    activate_version = args.activate if args.activate is not None else os.environ.get('ACTIVATE', 'false').lower() == 'true'
    percent_enabled = args.percent_enabled if args.percent_enabled is not None else int(os.environ.get('PERCENT_ENABLED', 0))

    if not all([api_user, api_token, fastly_key, corp_name, site_name, fastly_sid]):
        parser.error("Missing required arguments or environment variables.")

    if create_edge_security_service(api_user, api_token, corp_name, site_name) and confirm_compute_instance(api_user, api_token, corp_name, site_name):
        map_to_fastly_service(api_user, api_token, fastly_key, corp_name, site_name, fastly_sid, activate_version, percent_enabled)
