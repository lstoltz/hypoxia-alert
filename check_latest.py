#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author Linus Stoltz
@breif SModule for monitoring incoming dissolved oxygen data for the evidence of hypoxia
'''
import os
from glob import glob
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import fnmatch as fn
import pandas as pd
import numpy as np
import sys
from email_alert import Alert

load_dotenv()

LOG = 'last_ran.log'
SRC = os.getenv("SRC")
receiver_list = os.getenv("SENDER_LIST")
sender_email = os.getenv("EMAIL_USER")
app_pass = os.getenv("APP_PASS")

alert_threshold = 2 # Low oxygen threshold for sending the alert (mg/L)
fle = Path(LOG) # Make file if does not exist
fle.touch(exist_ok=True)

def find_csv():
    '''find all csv files in the SRC directory '''
    csvFiles = [file
                for path, subdir, files in os.walk(SRC) # find all csv files in a directory
                for file in glob(os.path.join(path, '*.csv'))]
    return csvFiles

def find_gps():
    '''find all csv files in the SRC directory '''
    gpsFiles = [file
                for path, subdir, files in os.walk(SRC) # find all csv files in a directory
                for file in glob(os.path.join(path, '*.gps'))]
    return gpsFiles

def check_log():
    '''Returns the last time this script was run, if never ran it will '''
    with open(LOG, "r") as fp:
        content = fp.readlines()
    fp.close()
    content = [x.strip() for x in content]
    if not content:
        update_log()
        with open(LOG, "r") as fp:
            content = fp.readlines()
        fp.close()
        content = [x.strip() for x in content]
        return content.pop()
    else:
        return content.pop()

def update_log():
    '''Updates the log file with the last time this alert script was run'''
    logged_time = datetime.utcnow()
    with open(LOG,"a") as fp:
        fp.write(str(logged_time)[:19])
        fp.write("\n")
    fp.close()

def strip_chars(dirty_string):
    '''Removes characters from the file id for easier comparision to time'''
    try:
        chars_to_remove = "_-: "  
        for char in chars_to_remove:
            dirty_string = dirty_string.replace(char, '')
        return int(dirty_string)
    except:
        sys.exit()

def get_new_files():
    last_ran = check_log()
    reference = strip_chars(last_ran)
    all_csv = find_csv()
    to_process = {}
    for file in all_csv:
        base_name = os.path.basename(file)
        if 'DissolvedOxygen' in base_name:
            split_string = base_name.partition('_Dissol')[0]
            date_string = split_string[-15:]
            try:
                date_string = strip_chars(date_string)
                if date_string > reference:
                    to_process.update({date_string: file})
            except:
                continue
    return to_process

def check_files():
    to_process = get_new_files()
    gps_files = find_gps()
    for file in to_process.values():
        df = pd.read_csv(file)
        do_values = df.iloc[:,1].values
        if len(do_values) < 6: # Skip files with less than an hour of data
            continue
        n_zeros = np.count_nonzero(do_values==0)
        sum_low_do = (alert_threshold > do_values).sum()
        if sum_low_do > 5: # if there are more than 5 values lower than 2mgL send the alert
            gps_file_path = find_coords(file, gps_files)
            alert = Alert(receiver_list, sender_email, app_pass, df, gps_file_path, file)
            alert.build_email()
            alert.send_email()
            

def find_coords(data_file, gps_files):
    base_name = os.path.basename(data_file)[:-20]
    gps_file_path = fn.filter(gps_files, str('*'+os.path.basename(base_name)+'*'))
    return gps_file_path

def main():
    check_files()
    update_log()

main()

