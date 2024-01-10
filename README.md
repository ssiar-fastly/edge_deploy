# NG WAF Deployment Script

This Python script automates the deployment of Next-Gen Web Application Firewall (NG WAF). It handles the creation of edge security services, confirms the creation of Compute instance resources, and maps your corp and site to an existing Fastly service.
Certainly! Here's a sample `README.md` file for your GitHub repository hosting the `edge_deploy.py` script:

---

## Prerequisites

Before you begin, ensure you have:

- Python 3.x installed on your machine.
- The `requests` library installed in Python. Install it using `pip install requests`.
- Access credentials for Signal Sciences (API User and API Token).
- A Fastly API key with write access.
- The Corp Name and Site Name for Signal Sciences.
- The Fastly Service ID (SID) to map.

## Setup

1. **Clone the Repository:**
   
   ```bash
   git clone https://github.com/your-username/edge-deploy.git
   cd edge-deploy
   ```

2. **Install Dependencies:**
   
   ```bash
   pip install requests
   ```

## Usage

The script can be executed with command-line arguments or environment variables. 

### Using Command-Line Arguments

Execute the script by passing all required parameters:

```bash
python edge_deploy.py --api_user [API_USER] --api_token [API_TOKEN] --fastly_key [FASTLY_KEY] --corp_name [CORP_NAME] --site_name [SITE_NAME] --fastly_sid [FASTLY_SID] [--activate] [--percent_enabled [0-100]]
```

Replace bracketed items with actual values.

### Using Environment Variables

1. Set the environment variables:

   ```bash
   export API_USER='your_api_user'
   export API_TOKEN='your_api_token'
   export FASTLY_KEY='your_fastly_key'
   export CORP_NAME='your_corp_name'
   export SITE_NAME='your_site_name'
   export FASTLY_SID='your_fastly_sid'
   export ACTIVATE='true' # or 'false'
   export PERCENT_ENABLED='10' # or any value between 0 and 100
   ```

2. Run the script:

   ```bash
   python edge_deploy.py
   ```

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request or open an issue for any changes you'd like to make.
