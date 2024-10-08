from twilio.rest import Client
from dotenv import load_dotenv
import os
from supabase import create_client
from datetime import datetime
from flash import store_message
import pandas as pd
from string import Template
import webbrowser



# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPBASE_URL = os.getenv('SUPBASE_URL')
SUPBASE_KEY = os.getenv('SUPBASE_KEY')
supabase = create_client(SUPBASE_URL, SUPBASE_KEY)

#We are considering offering this service in multiple languages English, Spanish, Korean etc with release of our next version. If you would be interested in this service.  Please text us back with the language of your choice.

sms_template = Template('''
Hi! $name
Good day!
To prepare for your follow-up appointment with Dr. Pallickal, please complete the brief Google Form linked here: $form. This will help us gather important information for your visit.  Your visit is cheduled for:
$aptmt.
We kindly ask that you fill out the form at least 48 hours before your appointment and arrive at the clinic at least 30 mins prior to the scheduled time . We are trying out a new AI system to increase the efficiency of our visits and to capture all the information relevant to your care.
 As this is a new system there may be some glitches initially, please feel free to ignore any questions if you don't feel they are appropriate to your care.
 If you have any questions or you would prefer not to get any text messages from this number, please contact us anytime at clinic.notes3@gmail.com.
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
    formatted_time = time_obj.strftime('%I:%M %p').lstrip('0')  # Remove leading zero

    # Create the formatted appointment string
    appt_string = f"{row['full_name'].strip()} {date} {formatted_time} PST"


    return appt_string

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


import argparse

if __name__ == "__main__":
    # Example usage: Send a Google Form link
    
    
    parser = argparse.ArgumentParser(description="Process an input file.")
    parser.add_argument('input_file', nargs='?', default='data/test_schedules_10-1-24.xlsx',
                        help='Input file to process (default: default.txt)')

    args = parser.parse_args()
    
    #fl = '/Users/jsubramanian/MyCode/SUS/Cofounders/MedTech/sample_json/10-2-24/patient_schedule_10-2-24.xlsx'
    
    fl= args.input_file
    
    print(f"Processing input file: {fl}")
    
    skiprows = 1
    df1 =  pd.read_excel(fl, skiprows=skiprows)
    #df1.rename(columns={col: 'Text' for col in df1.columns if 'Text' in col}, inplace=True)
        
    # Your original columns
    columns_to_check = ['first_name', 'URL', 'Text']

    # Get the matched columns
    
    matched_columns = fuzzy_column_match(df1, columns_to_check)
    
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

    
    import pdb; pdb.set_trace()
    for index, row in df1c.iterrows():
    
        try:
            print(f"Index: {index}, Row: {row}")
            
            name = row[matched_columns[0]]
            form_link = row[matched_columns[1]]
                
            phone_number = reformat_number(row[matched_columns[2]])
            
            flpath = fl
            #import pdb; pdb.set_trace()
            aptmtstr =  create_appointment_string(row, flpath)
            
            sms = sms_template.substitute(name=name,form=form_link,aptmt=aptmtstr)

    
            print(f"Texting {phone_number}  \n\n Form : {form_link} \n\n  Msg-len: {len(sms)} \n\n Msg: {sms} ")
            
            webbrowser.open(form_link)

            
            import pdb; pdb.set_trace();
            Txt_GoogleForm(sms,phone_number)
            
        except Exception as e:
            # Handle exceptions here
            import pdb; pdb.set_trace();
            print(f"An error occurred: {e}")
            continue
        
