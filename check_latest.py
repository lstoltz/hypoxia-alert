import os, sys, csv
from glob import glob
from os import listdir
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

load_dotenv()

LOG = os.getenv("LOG")
SRC = os.getenv("SRC")

fle = Path(LOG) # Make file if does not exist
fle.touch(exist_ok=True)

def find_csv():
    '''find all csv files in the SRC directory '''
    csvFiles = [file
                for path, subdir, files in os.walk(SRC) # find all csv files in a directory
                for file in glob(os.path.join(path, '*.csv'))]
    return csvFiles

def check_log():
    '''Returns the last time this script was run'''
    with open(LOG, "r") as fp:
        content = fp.readlines()
    fp.close()
    content = [x.strip() for x in content]
    return content.pop()

def update_log():
    '''Updates the log file with the last time this alert script was run'''
    logged_time = datetime.utcnow()
    with open(LOG,"a") as fp:
        fp.write(str(logged_time)[:19])
        fp.write("\n")
    fp.close()

def strip_chars(dirty_string):
    chars_to_remove = "_-: "  
    for char in chars_to_remove:
        dirty_string = dirty_string.replace(char, '')
    return int(dirty_string)


def get_new_files():
    last_ran = check_log()
    reference = strip_chars(last_ran)
    reference = 20220726100311
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
                    to_process.update({date_string: base_name})

            except:
                continue
    return to_process


print(get_new_files())


