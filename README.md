# hypoxia-alert
Takes realtime data collected by crab fleet and sends an email alert when and where a suspected low oxygen event occurs.
## Setup
Must create a .env variable which contains the following config information:
'''
SRC = path_to_the_incoming_data
LOG = name_of_created_log_file
PROJECT_ROOT = root_of_the_project

APP_PASS = password_for_email_account
SENDER_LIST = list_of_main_addresses to add more separate by comma
EMAIL_USER = email_address_sending_the_emails
'''
