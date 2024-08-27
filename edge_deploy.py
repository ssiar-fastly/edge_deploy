import os
import requests
import argparse
import json
import csv
import re
import time 

# Constants
BASE_URL = "https://dashboard.signalsciences.net/api/v0"
MAX_RETRIES = 3
RETRY_WAIT = 10
PROV_RETRY_WAIT = 45

def get_headers(ngwaf_user_email, ngwaf_token, fastly_token=None):
    headers = {
        "Content-Type": "application/json",
        "x-api-user": ngwaf_user_email,
        "x-api-token": ngwaf_token
    }
    if fastly_token:
        headers["Fastly-Key"] = fastly_token
    return headers

def retry_api_call(func):
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < MAX_RETRIES:
            response = func(*args, **kwargs)
            if isinstance(response, bool):
                return response
            if response.status_code == 200:
                return response
            elif response.status_code == 401:
                print("API call failed with Unauthorized (401) error. No retry will be attempted.")
                return response
            
            try:
                error_message_json = response.json()
                error_message = error_message_json.get("message", "")
            except json.JSONDecodeError:
                error_message = response.text

            if "failed to clone service" in error_message:
                print("Error: Failed to clone service. Suggestion: Check your Fastly API Token, or create a new one.")
                return response

            retries += 1
            print(f"API call failed, response code: {response.status_code}. Error details: {error_message}. Retrying in {RETRY_WAIT}s... (Retry {retries}/{MAX_RETRIES})")
            time.sleep(RETRY_WAIT)
        return response
    return wrapper

@retry_api_call
def sync_backend(ngwaf_user_email, ngwaf_token, fastly_token, corp_name, site_name, fastly_sid):
    url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}/edgeDeployment/{fastly_sid}/backends"
    response = requests.put(url, headers=get_headers(ngwaf_user_email, ngwaf_token, fastly_token))
    
    if response.status_code == 200:
        print(f"Successfully synchronized origins for site {site_name} with Fastly Service ID {fastly_sid}.")
    else:
        print(f"Failed to synchronize origins. Status Code: {response.status_code} - Details: {response.text}")
    return response

def process_sync_from_csv(csv_file_path, ngwaf_user_email, ngwaf_token, fastly_token, corp_name):
    with open(csv_file_path, mode='r') as read_file:
        reader = csv.reader(read_file)
        for row in reader:
            if len(row) < 2:
                continue
            site_name, fastly_sid = row[0], row[1]
            sync_backend(ngwaf_user_email, ngwaf_token, fastly_token, corp_name, site_name, fastly_sid)

@retry_api_call
def check_ngwaf_object_exists(ngwaf_user_email, ngwaf_token, fastly_token, corp_name, site_name):
    url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}/edgeDeployment"
    response = requests.get(url, headers=get_headers(ngwaf_user_email, ngwaf_token, fastly_token))
    
    if response.status_code == 200:
        response_json = response.json()
        agent_host_name = response_json.get("AgentHostName", "")
        
        # Use regex to match the expected pattern
        match = re.search(rf"se--{corp_name}--[a-z0-9]+\.edgecompute\.app", agent_host_name)
        if match:
            # Skip the first log message and only proceed with the operation
            return True
        else:
            print("NG WAF object does not exist.")
            return False
    elif response.status_code == 404:
        response_json = response.json()
        if response_json.get("message") == "edge deployment missing":
            print(f"NG WAF object does not exist for {site_name}, creating edge security object...")
            return False
        else:
            print(f"Failed to check NG WAF object. Status Code: {response.status_code} - Details: {response.text}")
            return False
    else:
        print(f"Failed to check NG WAF object. Status Code: {response.status_code} - Details: {response.text}")
        return False


@retry_api_call
def check_and_create_site(ngwaf_user_email, ngwaf_token, corp_name, site_name):
    site_exists_url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}"
    check_response = requests.get(site_exists_url, headers=get_headers(ngwaf_user_email, ngwaf_token))
    if check_response.status_code == 200:
        print(f"Site {site_name} already exists.")
        return check_response
    elif check_response.status_code in [400, 404]:
        # If the status code is 404, it's also treated as "Site not found"
        try:
            response_json = check_response.json()
            site_not_found_messages = ["Site not found", "Invalid resource request"]
            if response_json.get("message") in site_not_found_messages:
                print(f"Site {site_name} does not exist, creating...")
                create_site_url = f"{BASE_URL}/corps/{corp_name}/sites"
                site_details = {
                    "name": site_name,
                    "displayName": site_name,
                    "agentLevel": "log",
                    "blockHTTPCode": 406,
                    "blockDurationSeconds": 86400,
                    "blockRedirectURL": ""
                }
                create_response = requests.post(create_site_url, headers=get_headers(ngwaf_user_email, ngwaf_token), json=site_details)
                if create_response.status_code in [200, 201]:
                    print(f"Site {site_name} created successfully.")
                    return create_response
                else:
                    print(f"Failed to create site {site_name}. Status Code: {create_response.status_code} - Details: {create_response.text}")
                    return create_response
            else:
                print(f"Unexpected error message received. Message: {response_json.get('message')}")
                return check_response
        except json.JSONDecodeError:
            print("Failed to parse response as JSON.")
            return check_response
    else:
        print(f"Unexpected response while checking for site existence. Status Code: {check_response.status_code} - Details: {check_response.text}")
        return check_response

@retry_api_call
def create_edge_security_object(ngwaf_user_email, ngwaf_token, corp_name, site_name):
    print("Creating edge security object...")
    url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}/edgeDeployment"
    return requests.put(url, headers=get_headers(ngwaf_user_email, ngwaf_token))

@retry_api_call
def map_to_fastly_service(ngwaf_user_email, ngwaf_token, fastly_token, corp_name, site_name, fastly_sid, activate_version, percent_enabled, skip_wait=False, show_response_headers=False):
    if not skip_wait:
        print(f"Waiting {PROV_RETRY_WAIT} seconds for edge configuration to complete...")
        time.sleep(PROV_RETRY_WAIT)
    print("Mapping to Fastly service...")
    url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}/edgeDeployment/{fastly_sid}"
    payload = {"activateVersion": activate_version, "percentEnabled": percent_enabled}
    response = requests.put(url, headers=get_headers(ngwaf_user_email, ngwaf_token, fastly_token), json=payload)
    if show_response_headers:
        print(f"Response Headers: {response.headers}")
    return response

def process_single_site(ngwaf_user_email, ngwaf_token, fastly_token, corp_name, site_name, fastly_sid, activate_version, percent_enabled, show_response_headers=False):
    if check_ngwaf_object_exists(ngwaf_user_email, ngwaf_token, fastly_token, corp_name, site_name):
        print(f"NG WAF object exists for {site_name}, skipping edge object creation and wait time.")
        skip_wait = True
    else:
        print(f"NG WAF object does not exist for {site_name}, checking if site exists...")

        # Check if the site exists, and create it if it does not
        site_check_response = check_and_create_site(ngwaf_user_email, ngwaf_token, corp_name, site_name)
        if site_check_response.status_code not in [200, 201]:
            print(f"Failed to check or create site {site_name}. Status Code: {site_check_response.status_code} - Details: {site_check_response.text}")
            return

        print(f"Site {site_name} exists or was created successfully, proceeding to create edge security object...")
        skip_wait = False
        create_response = create_edge_security_object(ngwaf_user_email, ngwaf_token, corp_name, site_name)
        if create_response.status_code != 200:
            print(f"Failed to create edge security object. Status Code: {create_response.status_code} - Details: {create_response.text}")
            return

    map_response = map_to_fastly_service(ngwaf_user_email, ngwaf_token, fastly_token, corp_name, site_name, fastly_sid, activate_version, percent_enabled, skip_wait, show_response_headers)
    if map_response.status_code == 200:
        print("Edge deployment completed successfully.")
    else:
        print(f"Edge deployment failed during mapping to Fastly service: Status Code {map_response.status_code} - Details: {map_response.text}")

def process_sites_from_csv(csv_file_path, ngwaf_user_email, ngwaf_token, fastly_token, corp_name, activate_version, percent_enabled, show_response_headers=False):
    temp_file_path = csv_file_path + ".tmp"

    with open(csv_file_path, mode='r') as read_file, open(temp_file_path, mode='w', newline='') as write_file:
        reader = csv.reader(read_file)
        writer = csv.writer(write_file)

        for row in reader:
            if len(row) < 2:
                continue

            site_name, fastly_sid = row[0], row[1]
            process_single_site(ngwaf_user_email, ngwaf_token, fastly_token, corp_name, site_name, fastly_sid, activate_version, percent_enabled, show_response_headers)
            writer.writerow(row)

    os.replace(temp_file_path, csv_file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy NG WAF on Fastly Services")
    parser.add_argument('--ngwaf_user_email', default=os.environ.get('NGWAF_USER_EMAIL'), help='NGWAF user email')
    parser.add_argument('--ngwaf_token', default=os.environ.get('NGWAF_TOKEN'), help='NGWAF API token')
    parser.add_argument('--fastly_token', default=os.environ.get('FASTLY_TOKEN'), help='Fastly API token')
    parser.add_argument('--corp_name', default=os.environ.get('CORP_NAME'), help='Corporation name')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--provision', action='store_true', help='Provision sites from CSV file')
    group.add_argument('--sync-backend', action='store_true', help='Synchronize origins with Fastly backend')

    parser.add_argument('--csv_file', help='Path to CSV file with site name and Fastly SID, required for provisioning and sync-backend')
    parser.add_argument('--site_name', help='Site name, required for provisioning or synchronization')
    parser.add_argument('--fastly_sid', help='Fastly Service ID, required for provisioning or synchronization')
    parser.add_argument('--activate', type=lambda x: (str(x).lower() == 'true'), help='Activate the Fastly service version, required for provisioning')
    parser.add_argument('--percent_enabled', type=int, help='Percentage of traffic to send to NG WAF, required for provisioning')
    parser.add_argument('--show-response-headers', action='store_true', help='Flag to show response headers')

    args = parser.parse_args()

    if args.provision:
        if not all([args.csv_file, args.activate is not None, args.percent_enabled is not None]):
            print("Error: --csv_file, --activate, and --percent_enabled are required for provisioning.")
            exit(1)
        process_sites_from_csv(args.csv_file, args.ngwaf_user_email, args.ngwaf_token, args.fastly_token, args.corp_name, args.activate, args.percent_enabled, args.show_response_headers)
    
    elif args.sync_backend:
        if not args.csv_file:
            print("Error: --csv_file is required for backend synchronization.")
            exit(1)
        process_sync_from_csv(args.csv_file, args.ngwaf_user_email, args.ngwaf_token, args.fastly_token, args.corp_name)
