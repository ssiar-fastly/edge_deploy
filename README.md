# NG WAF Deployment Script

This Python script automates the deployment of Next-Gen Web Application Firewall (NG WAF). It handles the creation of edge security services, confirms the creation of Compute instance resources, and maps your corp and site to an existing Fastly service.

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

## Contributions

Contributions to this project are welcome! Feel free to fork the repository and submit pull requests.
