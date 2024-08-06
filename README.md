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
   Install Dependencies:
   ```bash
   pip3 install requests
   ```

## New Features and Improvements

### Advanced Error Handling and Retry Logic

- **Retry Mechanism:** The script now includes a retry mechanism for API calls, automatically retrying up to three times with a waiting period for transient network or server errors.
- **Enhanced Error Messages:** More informative error messages are provided, especially for HTTP 401 Unauthorized errors, to aid in troubleshooting.

### Edge Security Object Management

- **Automatic Creation:** If a site does not exist on NG WAF, the script now automatically creates an edge security object for it.
- **Mapping to Fastly Service:** Sites can be mapped to Fastly services more easily, with options to activate the Fastly service version immediately and to specify the percentage of traffic to be routed through the NG WAF.

### Flexible Deployment Options

- **Activate Version Option:** When mapping a site to a Fastly service, you can choose to activate the service version immediately with the `--activate` flag.
- **Traffic Ramping:** Control the percentage of traffic to route through the NG WAF using the `--percent_enabled` argument, allowing for gradual ramping up of traffic.

## Using `setup_env.zsh` to Update Local Terminal Environment

To streamline the process of setting environment variables, we have included a script called `setup_env.zsh`. This script will help you set up the necessary environment variables in your terminal session.

### Running the `setup_env.zsh` Script

1. **Make the script executable:**
   ```bash
   chmod +x setup_env.zsh
   ```
2. **Run the script:**
   ```bash
   source setup_env.zsh --update-file
   ```
   - The script will prompt you to enter values for `CORP_NAME`, `NGWAF_TOKEN`, and `FASTLY_TOKEN`.
   - If the `--update-file` flag is passed, it will also prompt for `site_name` and `service_id` and update `file.csv`.

3. **Reload the terminal environment:**
   After running the script, reload your `.zshrc` to apply the changes:
   ```bash
   source ~/.zshrc
   ```

### Using the Environment Variables

Once the environment variables are set, you can use the new function to load them in future sessions:

```bash
setenv_<CORP_NAME>
```

Replace `<CORP_NAME>` with the actual name you provided during the setup.

## CSV File Input

The script supports processing multiple sites from a CSV file. The CSV file should contain two columns: `site_name` and `fastly_sid`.

### Format of the CSV File

```csv
site_name,fastly_sid
site1,serviceID1
site2,serviceID2
...
```

### Using the CSV File

To use the CSV file, provide the file path as a command-line argument:

```bash
python3 edge_deploy.py --ngwaf_user_email 'your_ngwaf_user_email' --ngwaf_token 'your_ngwaf_token' --fastly_token 'your_fastly_token' --corp_name 'your_corp_name' --csv_file 'path/to/sites.csv' [--activate] [--percent_enabled <0-100>]
```

### Updating the CSV File with `setup_env.zsh`

If you use the `setup_env.zsh` script with the `--update-file` flag, it will prompt you for `site_name` and `service_id` and update `file.csv` accordingly.

```bash
source setup_env.zsh --update-file
```

---

## Usage

The script can be executed by providing command-line arguments or by setting environment variables.

### Using Command-Line Arguments

Execute the script by passing the required parameters:

```bash
python3 edge_deploy.py --ngwaf_user_email 'your_ngwaf_user_email' --ngwaf_token 'your_ngwaf_token' --fastly_token 'your_fastly_token' --corp_name 'your_corp_name' --site_name 'your_site_name' --fastly_sid 'your_fastly_service_id' [--activate] [--percent_enabled <0-100>]
```

Alternatively, you can provide a CSV file containing site names and Fastly Service IDs:

```bash
python3 edge_deploy.py --ngwaf_user_email 'your_ngwaf_user_email' --ngwaf_token 'your_ngwaf_token' --fastly_token 'your_fastly_token' --corp_name 'your_corp_name' --csv_file 'path/to/sites.csv' [--activate] [--percent_enabled <0-100>]
```

### Using Environment Variables

Set the following environment variables, then run the script without specifying the parameters:

```bash
export NGWAF_USER_EMAIL='your_ngwaf_user_email'
export NGWAF_TOKEN='your_ngwaf_token'
export FASTLY_TOKEN='your_fastly_token'
export CORP_NAME='your_corp_name'
export SITE_NAME='your_site_name' # Required if not using a CSV file
export FASTLY_SID='your_fastly_service_id' # Required if not using a CSV file
export ACTIVATE='true' # Optional, default is false
export PERCENT_ENABLED='10' # Optional, default is 0
```

Then, execute the script:

```bash
python3 edge_deploy.py
```

### Example Scenarios

- **Deploying with Partial Traffic Ramping:**
  ```bash
  python3 edge_deploy.py --ngwaf_user_email 'user@example.com' --ngwaf_token 'token123' --fastly_token 'fastlykey123' --corp_name 'MyCorp' --site_name 'MySite' --fastly_sid 'serviceID' --activate --percent_enabled 25
  ```

This command deploys the NG WAF with 25% of traffic initially routed through the new setup.

- **Deploying without Activating the Fastly Service:**
  ```bash
  python3 edge_deploy.py --ngwaf_user_email 'user@example.com' --ngwaf_token 'token123' --fastly_token 'fastlykey123' --corp_name 'MyCorp' --site_name 'MySite' --fastly_sid 'serviceID'
  ```

This will set up the NG WAF without activating the Fastly service version, allowing for manual activation later.

### Watch demo video
Check out this walkthrough of our project: https://www.loom.com/share/88977b2ac2d747fd89b842ece5ee06e3
Batch deployment update: https://www.loom.com/share/5aa133387d1e4872be216b235b98941c

## Contributions

Contributions to this project are welcome! Feel free to fork the repository and submit pull requests.

## Contact

Sina Siar - [@ssiar](https://linkedin.com/in/ssiar) - ssiar@fastly.com
