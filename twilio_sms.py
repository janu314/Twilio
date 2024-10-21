'''  python twilio_sms.py '/Users/jsubramanian/MyCode/SUS/Cofounders/MedTech/sample_json/10-17-24/patient_schedule_10-17-24.xlsx'
'''

from twilio.rest import Client
from dotenv import load_dotenv
import os
from supabase import create_client
from datetime import datetime
from flash import store_message
import pandas as pd
from string import Template
import webbrowser
import numpy as np
import os
import pyshorteners




# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPBASE_URL = os.getenv('SUPBASE_URL')
SUPBASE_KEY = os.getenv('SUPBASE_KEY')
supabase = create_client(SUPBASE_URL, SUPBASE_KEY)

#We are considering offering this service in multiple languages English, Spanish etc. If you would be interested; pls. text us back with the language of your choice.

sms_template1 = Template('''
Hi! $name
Good day!
To prepare for your follow-up appt. with Dr. Pallickal, pls. complete this brief Google Form : $form. This will help us gather important information for your visit scheduled on:
$aptmt.
 We are considering offering this service in multiple languages English, Spanish etc. If you would be interested; pls. text us back the language of your choice.
We kindly ask that you fill out the form at least 24 hours before and arrive at least 30 mins prior to the scheduled appointment . We are trying out a new AI system to increase the efficiency of our visits and to capture all the information relevant to your care.
 As this is a new system there may be some glitches initially, pls. feel free to ignore any questions if you don't feel they are appropriate to your care.
 If you have any questions or you would prefer not to get any text messages from this number, please contact us anytime at clinic.notes3@gmail.com.
Thank you!
Best,
Norinne
Medical Assistant ''')


sms_template2 = Template('''
Hello $name\n

Good day! This a friendly reminder for your upcoming appointment (tomorrow) with  Dr. Pallickal.  Your appointment details are as follows:\n
$aptmt.\n

We kindly request you to arrive at least 30 mins prior to the scheduled appointment.\n

This is an automated message; if you have any questions or you would prefer not to get any text messages from this number, please contact us anytime at clinic.notes3@gmail.com.\n

Thank you!
Best,
Norinne
Medical Assistant ''')



import pandas as pd
from datetime import datetime

import pandas as pd
from fuzzywuzzy import process


def fuzzy_column_match(df, columns, threshold=80):
    """
    Match columns using fuzzy string matching.
    
    :param df: DataFrame
    :param columns: List of column names to match
    :param threshold: Minimum similarity score to consider a match (0-100)
    :return: List of matched column names
    """
    matched_columns = []
    
    for col in columns:
        # Use process.extractOne to find the best match
        best_match = process.extractOne(col, df.columns)
        if best_match[1] >= threshold:
            matched_columns.append(best_match[0])
    
    return matched_columns


import pandas as pd

def case_insensitive_column_match(df, columns):
    """
    Match columns case-insensitively and handle variations.
    
    :param df: DataFrame
    :param columns: List of column names to match
    :return: List of matched column names
    """
    matched_columns = []
    df_columns_lower = [col.lower() for col in df.columns]
    
    for col in columns:
        # Check for exact match (case-insensitive)
        if col.lower() in df_columns_lower:
            matched_columns.append(df.columns[df_columns_lower.index(col.lower())])
        else:
            # Check for partial matches
            import pdb; pdb.set_trace();
            partial_matches = [df_col for df_col in df.columns
                               if col.lower() in df_col.lower()]
            if partial_matches:
                matched_columns.extend(partial_matches)
    
    return matched_columns



def create_appointment_string(row, file_path):
    """
    Create a formatted appointment string from a DataFrame row and file path.
    
    :param row: A pandas Series containing appointment information
    :param file_path: String path to the Excel file
    :return: Formatted appointment string
    """
    # Extract the date from the file name
    date_str = file_path.split('/')[-1].split('_')[-1].split('.')[0]
    date = datetime.strptime(date_str, '%m-%d-%y').strftime('%m/%d/%y')
    
    #import pdb; pdb.set_trace();
    # Parse the time and add AM/PM
    time_obj = datetime.strptime(row['time'], '%H:%M')
    
    # Get the hour as an integer
    hour = time_obj.hour

    # Custom logic to assign AM/PM
    if 8 <= hour <= 11:
        period = 'AM'  # Times between 1:00 and 6:00 are likely PM
    else:
        period = 'PM'  # All other times default to AM (you can tweak this rule as needed)

    # Format the time without leading zeros for hours
    formatted_time = f'{hour}:{time_obj.strftime("%M")} {period}'

    print(formatted_time)
    #formatted_time = time_obj.strftime('%I:%M %p').lstrip('0')  # Remove leading zero

    # Create the formatted appointment string
    #appt_string1 = f"{row['full_name'].strip()} {date} {formatted_time} PST"

    fname = row['full_name'].strip()
    datestr = f"Date : {date}"
    
    ftime = f"{formatted_time} PST"
    
    appt_string = f"{fname}\n{datestr}\n{ftime}"

    return appt_string, fname

# Example usage:
# Assuming df is your DataFrame and file_path is the path to your Excel file
# file_path = '/Users/jsubramanian/MyCode/SUS/Cofounders/MedTech/sample_json/10-2-24/patient_schedule_10-2-24.xlsx'
# for index, row in df.iterrows():
#     print(create_appointment_string(row, file_path))





import re

def reformat_number(phone):
    # Use regex to extract all digits from the phone number
    digits = re.sub(r'\D', '', phone)
    
    # Ensure the number has 10 digits (US phone number)
    if len(digits) == 10:
        return f'+1{digits}'
    elif len(digits) == 11 and digits.startswith('1'):
        return f'+{digits}'
    else:
        raise ValueError("Invalid phone number format")



def Txt_GoogleForm(msg, my_phone_number = os.getenv('MY_PHONE_NUMBER')):
    # Get Twilio credentials and phone numbers from environment variables
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

    # Check if the environment variables are loaded correctly
    if not all([account_sid, auth_token, twilio_phone_number, my_phone_number]):
        print("Environment variables are missing or incorrect.")
        return

    # Initialize Twilio client
    client = Client(account_sid, auth_token)

    # Create and send a message
    outgoing_message = f"{msg}"
    message = client.messages.create(
        body=outgoing_message,
        from_=twilio_phone_number,
        to=my_phone_number  
    )

    # Print the message SID for debugging/logging
    print(f"Message SID: {message.sid}")

    # Store the outgoing message in Supabase
    store_message(twilio_phone_number, my_phone_number, outgoing_message)


def send_follow_up_forms(df1,fpath):

    # Your original columns
    columns_to_check = ['first_name', 'URL', 'Text']

    # Get the matched columns
    
    matched_columns = fuzzy_column_match(df1, columns_to_check)
    df1[matched_columns] = df1[matched_columns].replace(' ', np.nan)

    
    # Drop rows with NaN in the matched columns
    df1c = df1.dropna(subset=matched_columns)
    
    print(f"Matched columns: {matched_columns}")
    print(f"Shape before dropping: {df1.shape}")
    print(f"Shape after dropping: {df1c.shape}")
    
    # Identify rows with NaN in the matched columns
    rows_with_nan = df1[df1[matched_columns].isna().any(axis=1)]

    # Print dropped rows
    print("\nDropped rows:")
    print(rows_with_nan)

    # Print the number of dropped rows
    print(f"\nNumber of rows dropped: {len(rows_with_nan)}")

    start = 1
    import pdb; pdb.set_trace()
    for index, row in df1c.iterrows():
    
        try:
            print(f"Index: {index}, Row: {row}")
            
            if(index < start):
                continue
            
            name = row[matched_columns[0]]
            form_link = row[matched_columns[1]]
            
            # Create an instance of Shortener
            s = pyshorteners.Shortener()


            # Shorten the URL
            short_url = s.tinyurl.short(form_link)

            #import pdb; pdb.set_trace()
            print('Shortened URL:', short_url)

                
            phone_number = reformat_number(row[matched_columns[2]])
            
            #import pdb; pdb.set_trace()
            aptmtstr, fname =  create_appointment_string(row, fpath)
            
            sms = sms_template1.substitute(name=fname,form=short_url,aptmt=aptmtstr)

    
            print(f"Texting {phone_number}  \n\n Form : {short_url} \n\n  Msg-len: {len(sms)} \n\n Msg: {sms} ")
            
            webbrowser.open(short_url)

            
            import pdb; pdb.set_trace();
            Txt_GoogleForm(sms,phone_number)
            
        except Exception as e:
            # Handle exceptions here
            import pdb; pdb.set_trace();
            print(f"An error occurred: {e}")
            continue
            

def send_aptmt_reminder(df1,fpath):

    # Your original columns
    columns_to_check = ['first_name', 'Text']

    # Get the matched columns

    matched_columns = fuzzy_column_match(df1, columns_to_check)
    
    df1[matched_columns] = df1[matched_columns].replace(' ', np.nan)
    
    # Drop rows with NaN in the matched columns
    df1c = df1.dropna(subset=matched_columns)
    
    print(f"Matched columns: {matched_columns}")
    print(f"Shape before dropping: {df1.shape}")
    print(f"Shape after dropping: {df1c.shape}")
    
    # Identify rows with NaN in the matched columns
    rows_with_nan = df1[df1[matched_columns].isna().any(axis=1)]

    # Print dropped rows
    print("\nDropped rows:")
    print(rows_with_nan)

    # Print the number of dropped rows
    print(f"\nNumber of rows dropped: {len(rows_with_nan)}")

    
    start = 0
    import pdb; pdb.set_trace()
    for index, row in df1c.iterrows():
    
        try:
            print(f"Index: {index}, Row: {row}")
            
            if(index < start):
                continue
                
                
            phone_number = reformat_number(row[matched_columns[1]])
            
            #flpath = fl
            #import pdb; pdb.set_trace()
            aptmtstr, fname =  create_appointment_string(row, fpath)
            
            sms = sms_template2.substitute(name=fname,aptmt=aptmtstr)

    
            print(f"Texting {phone_number}   \n\n  Msg-len: {len(sms)} \n\n Msg: {sms} ")
            
            
            import pdb; pdb.set_trace();
            Txt_GoogleForm(sms,phone_number)
            
                
            
        except Exception as e:
            # Handle exceptions here
            import pdb; pdb.set_trace();
            print(f"An error occurred: {e}")
            continue
    
        

    

import argparse
import subprocess

import tkinter as tk
from tkinter import filedialog
import os

if __name__ == "__main__":
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Set the default directory
    default_dir = '/Users/jsubramanian/MyCode/SUS/Cofounders/MedTech/sample_json/'

    # Open the file dialog
    fpath = filedialog.askopenfilename(
        initialdir=default_dir,
        title="Select input file",
        filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"))
    )
    
    print(f"Processing input file: {fpath}")
    
    # Check if the file exists
    if os.path.exists(fpath):
        # Open the file
        # Open the file with the default application
        # Open the file with the default application
        subprocess.run(['open', fpath])

    else:
        print(f"The file {fpath} does not exist.")

    
    skiprows = 1
    df1 =  pd.read_excel(fpath, skiprows=skiprows)
    
    #Fix the DOB
    df1['DOB'] = pd.to_datetime(df1['DOB'], errors='coerce')  # errors='coerce' will handle invalid dates
    
    # Step 2: Calculate age
    today = pd.to_datetime(datetime.today().date())  # Get today's date
    df1['age'] = df1['DOB'].apply(lambda x: (today - x).days // 365 if not pd.isnull(x) else None)

    # Step 3: Display the DataFrame with the new 'age' column
    print(df1[['DOB', 'age']])
    
    import pdb; pdb.set_trace();
    
    send_aptmt_reminder(df1,fpath)
    
    #send_follow_up_forms(df1,fpath)
    
    #  Try sending follow reminder texts
    
    
