import os
import requests
import argparse
import time

# Constants
BASE_URL = "https://dashboard.signalsciences.net/api/v0"
MAX_RETRIES = 3
RETRY_WAIT = 10

def get_headers(api_user, api_token, fastly_key=None):
    # Generate headers for API requests
    headers = {"Content-Type": "application/json", "x-api-user": api_user, "x-api-token": api_token}
    if fastly_key:
        headers["Fastly-Key"] = fastly_key
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
            print(f"API call failed, response code: {response.status_code}. Retrying in {RETRY_WAIT}s... (Retry {retries}/{MAX_RETRIES})")
            time.sleep(RETRY_WAIT)
        return response
    return wrapper

@retry_api_call
def create_edge_security_object(api_user, api_token, corp_name, site_name):
    # Create an edge security object for the specified corp and site
    print("Creating edge security object...")
    url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}/edgeDeployment"
    return requests.put(url, headers=get_headers(api_user, api_token))

@retry_api_call
def map_to_fastly_service(api_user, api_token, fastly_key, corp_name, site_name, fastly_sid, activate_version, percent_enabled):
    # Map the corp and site to a Fastly service and synchronize origins
    print("Waiting 60 seconds for edge configuration to complete...")
    time.sleep(60)
    print("Mapping to Fastly service...")
    url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}/edgeDeployment/{fastly_sid}"
    payload = {"activateVersion": activate_version, "percentEnabled": percent_enabled}
    return requests.put(url, headers=get_headers(api_user, api_token, fastly_key), json=payload)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy NG WAF on Magento Fastly Services")
    parser.add_argument('--api_user', help='API user email')
    parser.add_argument('--api_token', help='API token')
    parser.add_argument('--fastly_key', help='Fastly API key')
    parser.add_argument('--corp_name', help='Corporation name')
    parser.add_argument('--site_name', help='Site name')
    parser.add_argument('--fastly_sid', help='Fastly Service ID')
    parser.add_argument('--activate', type=lambda x: (str(x).lower() == 'true'), help='Activate the Fastly service version')
    parser.add_argument('--percent_enabled', type=int, help='Percentage of traffic to send to NG WAF', default=None)

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

    if create_edge_security_object(api_user, api_token, corp_name, site_name):
        print("Edge security object created successfully.")
        response = map_to_fastly_service(api_user, api_token, fastly_key, corp_name, site_name, fastly_sid, activate_version, percent_enabled)
        if response.status_code == 200:
            print("Edge deployment completed successfully.")
        else:
            print(f"Edge deployment failed: {response.text}")
    else:
        print("Failed to create edge security object.")
