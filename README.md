# hypoxia-alert
Takes realtime data collected by crab fleet and sends an email alert when and where a suspected low oxygen event occurs.
## Setup
Must create a ```.env``` variable at the project root which contains the following config information:
```
SRC = path_to_the_incoming_data
LOG = name_of_created_log_file
PROJECT_ROOT = root_of_the_project

APP_PASS = password_for_email_account
SENDER_LIST = list_of_main_addresses to add more separate by comma
EMAIL_USER = email_address_sending_the_emails
```

## How it works
The script when ran will look at the log file for the last time the script was ran, if this is the first time being run it will generate the log file. The script will then look for all files with times after the last log entry. With the list of new files to check the script will read those data files and determine if and how many occurances of oxygen values are below 2 mg/L which is the threshold for hypoxia.

If a file is new and contains hypoxic values, the script will construct an email which includes GPS location, file name, as well as a plot of the data for quick visualization. 
