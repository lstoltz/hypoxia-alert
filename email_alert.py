import smtplib, ssl, os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
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
        self.resources = os.path.join(os.getenv("PROJECT_ROOT"), "src", "resources",)
        self.file_name = file
    
    def build_email(self):
        # TODO: 
        #   add inline plot to body of email
        gps = self.read_gps()
        img_path = self.create_plot()
        file_id = os.path.basename(self.file_name)
        subject = "Hypoxia Alert"
        body="""\
            <html>
                <head></head>
                <body>
                    Hypoxia potentially detected!<br>
                    File ID: {file_id} <br>
                    Location: {gps} <br>
            </html>
            """.format(gps=gps, file_id=file_id)
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = ", ".join(self.receiver_list)
        message["Subject"] = subject

        message.attach(MIMEText(body, "html"))

        self.text = message.as_string()

        with open(img_path, 'rb') as f:
            mime = MIMEImage(f.read())
            f.close()
            # mime.add_header('Content-Disposition', 'attachment', filename=img_path)
            # mime.add_header('X-Attachment-Id', '0')
            mime.add_header('Content-ID', '<0>')
            # read attachment file content into the MIMEBase object
            
            
    # encode with base64
            # encoders.encode_base64(mime)
    # add MIMEBase object to MIMEMultipart object
            message.attach(mime)
    def send_email(self):
        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(self.sender_email, self.app_pass)
            server.sendmail(self.sender_email, self.receiver_list, self.text)
            server.quit()

    def read_gps(self):
        with open(self.gps_file[0], 'r') as fp:
            gps_data = fp.readlines()
            gps_data = ' '.join(gps_data).strip()
        fp.close()
        return gps_data

    def create_plot(self):
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

        # --- added this part --
        ax.axhspan(0, 2, facecolor='0.5', alpha=0.3)
        # ax2.axhspan(0, 1.4, facecolor='0.5', alpha=0.3)
        ax.set_ylim(0, 10)	# resetting the ylim to be based on oxygen values, not including grey bar
        #----------
        #         
       
        fig.tight_layout()    # misc figure formatting and date stuff
        ax.xaxis_date()
        myFmt = mdates.DateFormatter("%m-%d-%y")
        ax.xaxis.set_major_formatter(myFmt)
        fig.autofmt_xdate()

        Path(self.resources).mkdir(parents=True, exist_ok=True)
        file_name = os.path.basename(self.file_name)[:-20] + ".png"
        plt.savefig(os.path.join(self.resources, file_name))
        plt.close()
        
        self.image_path = self.resources + os.path.sep + file_name
        return self.image_path
