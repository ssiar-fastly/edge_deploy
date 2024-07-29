#!/bin/zsh

# Function to prompt for input and exit if empty
prompt_for_input() {
    local prompt_message="$1"
    local input_var
    read "input_var?$prompt_message: "
    if [[ -z "$input_var" ]]; then
        echo "Input cannot be empty. Exiting."
        exit 1
    fi
    echo "$input_var"
}

# Function to update file.csv
update_file_csv() {
    local site_name=$(prompt_for_input "Enter value for site_name")
    local service_id=$(prompt_for_input "Enter value for service_id")

    # Override file.csv with new values
    echo "$site_name,$service_id" > file.csv
}

# Check for --update-file flag
UPDATE_FILE=false
if [[ "$1" == "--update-file" ]]; then
    UPDATE_FILE=true
fi

# Prompt for values
CORP_NAME=$(prompt_for_input "Enter value for CORP_NAME")
NGWAF_USER_EMAIL="ssiar+${CORP_NAME}@fastly.com"
NGWAF_TOKEN=$(prompt_for_input "Enter value for NGWAF_TOKEN")
FASTLY_TOKEN=$(prompt_for_input "Enter value for FASTLY_TOKEN")

# Create the environment file
ENV_FILE=~/.env_configs/${CORP_NAME}.env
cat <<EOL > $ENV_FILE
export NGWAF_USER_EMAIL=${NGWAF_USER_EMAIL}
export NGWAF_TOKEN=${NGWAF_TOKEN}
export FASTLY_TOKEN=${FASTLY_TOKEN}
export CORP_NAME=${CORP_NAME}
EOL

# Function to modify .zshrc
add_setenv_function() {
    local corp_name="$1"
    local zshrc_file=~/.zshrc

    # Add function to .zshrc
    if ! grep -q "setenv_${corp_name}" "$zshrc_file"; then
        echo -e "\nfunction setenv_${corp_name}() {\n    source ~/.env_configs/${corp_name}.env\n}" >> $zshrc_file
    fi
}

# Call the function to add to .zshrc
add_setenv_function $CORP_NAME

# Source the new environment file to set the variables immediately
source $ENV_FILE

# Update file.csv if --update-file flag is passed
if $UPDATE_FILE; then
    update_file_csv
fi

echo "Configuration for $CORP_NAME has been set and the environment variables are loaded."
if $UPDATE_FILE; then
    echo "file.csv has been updated with site_name and service_id."
fi


# Notify user to reload .zshrc to pick up the new function
echo "Please run 'source ~/.zshrc' to load the new environment function into your current session."

echo "Use 'setenv_${CORP_NAME}' to load the environment variables in the future."

echo "Use the python command below to execute the NGWAF onboarding:"
echo "python3 edge_deploy.py --csv_file file.csv --activate false --percent_enabled 100"
