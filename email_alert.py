#!/usr/bin/env python
# -*- coding: utf-8 -*-
#@author Linus Stoltz
#@breif Helper class for generating and sending the alert email
import smtplib, os
from email.message import EmailMessage
from email.utils import make_msgid
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
from pathlib import Path
import pandas as pd

class Alert:
    resources = None
    def __init__(self, receiver_list, sender_email, app_pass, dataframe, gps_file, file):
        self.receiver_list = [receiver_list]
        self.sender_email = sender_email
        self.app_pass = app_pass
        self.df = dataframe
        self.gps_file = gps_file
        self.resources = os.path.join(os.getcwd(), "src", "resources",)
        self.file_name = file
    
    def build_email(self):
        '''Sets up the image path and location information to construct the email alert'''
        subject = 'Hypoxia Alert'
        self.text = ('Hypoxia dectected at: %s.<br>\nFile ID: %s<br>\n*Data has not been subjected to QA/QC and should be treated as such.'
                    % (self.read_gps(), os.path.basename(self.file_name)))
        
        self.footer_text = 'If you wish to be removed from hypoxia alerts please contact the author (stoltzl@oregonstate.edu) '

        img_path = self.create_plot()

        self.msg = EmailMessage()
        self.msg.add_header('From', self.sender_email)
        self.msg.add_header('Reply-To', self.sender_email)
        self.msg.add_header('Subject', subject)

        attachment_cid = make_msgid()

        self.msg.set_content('%s<br/><img src="cid:%s"/<br/><br>%s' % (
        self.text, attachment_cid[1:-1], self.footer_text),'html') # need to add image as HTML

        with open(img_path, 'rb') as fp:
            self.msg.add_related(
            fp.read(), 'image','png', cid=attachment_cid)
        fp.close()

    def send_email(self):
        '''Log in to server using secure context and send email'''
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.app_pass)
            server.sendmail(self.sender_email, self.receiver_list, self.msg.as_string().encode('utf-8'))
            server.close()
        except smtplib.SMTPException as e:
            print('SMTP error: %s' % e)

    def read_gps(self):
        ''' Utility function to read the gps location'''
        with open(self.gps_file[0], 'r') as fp:
            gps_data = fp.readlines()
            gps_data = ' '.join(gps_data).strip()
        fp.close()
        return gps_data

    def create_plot(self):
        ''' Generates the plot for the low oxygen data file'''
        fig, ax = plt.subplots()
        color = 'tab:blue'
        
        ax.plot(pd.to_datetime(self.df['ISO 8601 Time']),self.df['Dissolved Oxygen (mg/l)'], color=color)
        ax.set_ylabel('Dissolved oxygen (mg/L)', color=color)
        ax.tick_params(axis='y', labelcolor=color)

        ax2 = ax.twinx()  # creating second axis for temperature
        color2 = 'tab:red'
        ax2.set_ylabel('Temperature ($^\circ$C)', color=color2)
        ax2.plot(pd.to_datetime(self.df['ISO 8601 Time']),self.df['DO Temperature (C)'], color=color2)
        ax2.tick_params(axis='y', labelcolor=color2)
        ax.axhspan(0, 2, facecolor='0.5', alpha=0.3)
        ax.set_ylim(0, 10)	# resetting the ylim to be based on oxygen values, not including grey bar
       
        fig.tight_layout()    # misc figure formatting and date stuff
        ax.xaxis_date()
        myFmt = mdates.DateFormatter("%m-%d-%y")
        ax.xaxis.set_major_formatter(myFmt)
        fig.autofmt_xdate()

        Path(self.resources).mkdir(parents=True, exist_ok=True) # save image path for use in email
        file_name = os.path.basename(self.file_name)[:-20] + ".png"
        plt.savefig(os.path.join(self.resources, file_name))
        plt.close()
        
        self.image_path = self.resources + os.path.sep + file_name
        return self.image_path
