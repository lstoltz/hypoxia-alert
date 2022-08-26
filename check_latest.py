import os, sys, csv
from glob import glob
from os import listdir
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

LOG = os.getenv("LOG")
SRC = os.getenv("SRC")

def find_csv(SRC):
    # find all csv files in the SRC directory
    csvFiles = [file
                for path, subdir, files in os.walk(SRC) # find all csv files in a directory
                for file in glob(os.path.join(path, '*.csv'))]
    return csvFiles

def load_log(LOG):
    header = ['time_processed', 'number_processed', 'number_alert']
    with open(LOG, "w+") as fp:
        writer = csv.writer(fp, delimiter= ',')
        writer.writerow(header)
    fp.close()
    df = pd.read_csv(LOG)
    return df
def update_log(df, LOG):
    df.loc[len(df.index)] = ['2022-08-25','7','3']
    df.to_csv(LOG)


files = find_csv(SRC)
df = load_log(LOG)
update_log(df, LOG)

