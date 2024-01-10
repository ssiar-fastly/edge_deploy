# NG WAF Deployment Script

This Python script automates the deployment of Next-Gen Web Application Firewall (NG WAF). It handles the creation of edge security services, confirms the creation of Compute instance resources, and maps your corp and site to an existing Fastly service.

## Prerequisites

Before you begin, ensure you have the following:

- Python 3 installed on your machine.
- `requests` library installed. You can install it using `pip install requests`.
- Access credentials for Signal Sciences (API User and API Token).
- A Fastly API key with write access.
- The Corp Name and Site Name for the Signal Sciences dashboard.
- The Fastly Service ID (SID) you wish to map to.

## Installation

Clone the repository and navigate to the directory containing the script:

```bash
git clone https://github.com/ssiar-fastly/edge_deploy
cd edge_deploy
```

## Usage

The script can be executed from the command line by passing the required parameters. Here's how to use the script:

```bash
python edge_deploy.py <api_user> <api_token> <fastly_key> <corp_name> <site_name> <fastly_sid> [--activate] [--percent_enabled <0-100>]
```

Replace `<api_user>`, `<api_token>`, `<fastly_key>`, `<corp_name>`, `<site_name>`, and `<fastly_sid>` with your actual Signal Sciences and Fastly details.

### Arguments

- `api_user`: Email associated with the Signal Sciences API user.
- `api_token`: API token for Signal Sciences.
- `fastly_key`: Fastly API key with write access.
- `corp_name`: Name of the corporation in Signal Sciences.
- `site_name`: Name of the site in Signal Sciences.
- `fastly_sid`: Fastly Service ID to map.
- `--activate`: (Optional) Flag to activate the Fastly service version immediately.
- `--percent_enabled`: (Optional) Integer value between 0 and 100 to set the percentage of traffic to send to the NG WAF.

### Examples

To deploy NG WAF without activating the Fastly service version:

```bash
python edge_deploy.py user@example.com token123 fastlykey123 corp-example site-example fastlyserviceid
```

To deploy NG WAF and activate the Fastly service version with 10% traffic:

```bash
python edge_deploy.py user@example.com token123 fastlykey123 corp-example site-example fastlyserviceid --activate --percent_enabled 10
```

## Support

For issues and feature requests, please file an issue in the GitHub repository issue tracker.
