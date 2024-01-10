# NG WAF Deployment Script

This Python script automates the deployment of Next-Gen Web Application Firewall (NG WAF). It handles the creation of edge security compute object and maps your corp and site to an existing Fastly service.

---

## Prerequisites

Before running the script, ensure the following are installed and set up:

- Python 3.x
- `requests` library for Python (Installable via `pip3 install requests`)
- Access credentials for NG WAF and Fastly

## Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/ssiar-fastly/edge_deploy.git
   cd edge_deploy
   ```

2. **Install Dependencies:**
   ```bash
   pip3 install requests
   ```

## Usage

The script can be executed by providing command-line arguments or by setting environment variables.

### Using Command-Line Arguments

Execute the script by passing the required parameters:

```bash
python3 edge_deploy.py --ngwaf_user_email 'your_ngwaf_user_email' --ngwaf_token 'your_ngwaf_token' --fastly_token 'your_fastly_token' --corp_name 'your_corp_name' --site_name 'your_site_name' --fastly_sid 'your_fastly_service_id' [--activate] [--percent_enabled <0-100>]
```

### Using Environment Variables

Alternatively, you can set the following environment variables:

```bash
export NGWAF_USER_EMAIL='your_ngwaf_user_email'
export NGWAF_TOKEN='your_ngwaf_token'
export FASTLY_TOKEN='your_fastly_token'
export CORP_NAME='your_corp_name'
export SITE_NAME='your_site_name'
export FASTLY_SID='your_fastly_service_id'
export ACTIVATE='true' # Optional, default is false
export PERCENT_ENABLED='10' # Optional, default is 0
```

Then, run the script without specifying the parameters:

```bash
python3 edge_deploy.py
```


## Example Scenarios

1. **Deploying with Partial Traffic Ramping:**
   ```bash
   python3 edge_deploy.py --ngwaf_user_email 'user@example.com' --ngwaf_token 'token123' --fastly_token 'fastlykey123' --corp_name 'MyCorp' --site_name 'MySite' --fastly_sid 'serviceID' --activate --percent_enabled 25
   ```
   This command deploys the NG WAF with 25% of traffic initially routed through the new setup.

2. **Deploying without Activating the Fastly Service:**
   ```bash
   python3 edge_deploy.py --ngwaf_user_email 'user@example.com' --ngwaf_token 'token123' --fastly_token 'fastlykey123' --corp_name 'MyCorp' --site_name 'MySite' --fastly_sid 'serviceID'
   ```
   This will set up the NG WAF without activating the Fastly service version, allowing for manual activation later.

3. **Deploying with Environment Variables:**
   First, set the environment variables, then run the script:
   ```bash
   python3 edge_deploy.py
   ```
   This approach is useful for automation scripts or continuous integration/deployment systems.


## Contributions

Contributions to this project are welcome! Feel free to fork the repository and submit pull requests.
