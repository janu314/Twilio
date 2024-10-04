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


sms_template = Template('''
Hi! $name
Good day!
To prepare for your follow-up appointment with Dr. Pallickal, please complete the brief Google Form linked here: $form. This will help us gather important information for your visit.
We kindly ask that you fill out the form at least 24 hours before your appointment. We are trying out a new AI system to increase the efficiency of our visits and to capture all the information relevant to your care.  As this is a new system there may be some glitches initially, please feel free to ignore any questions if you don't feel they are appropriate to your care. This is an automated message, If you have any questions or you would prefer not to get any text messages from this number, please contact us anytime at clinic.notes3@gmail.com.
Thank you!
Best,
Norinne
Medical Assistant ''')



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

if __name__ == "__main__":
    # Example usage: Send a Google Form link
    
    
    fl = '/Users/jsubramanian/MyCode/SUS/Cofounders/MedTech/sample_json/10-2-24/patient_schedule_10-2-24.xlsx'
    
    
    df1 =  pd.read_excel(fl, skiprows=1)
    df1 = df1.dropna(subset=['first_name','URL', 'Text' ])
    
    import pdb; pdb.set_trace()
    for index, row in df1.iterrows():
    
        try:
            print(f"Index: {index}, Row: {row}")
            
            name = row['first_name']
            form_link = row['URL']
                
            phone_number = reformat_number(row['Text'])
            #phone_number = '+16464162744' ; name = 'Janu'
            
            sms = sms_template.substitute(name=name,form=form_link)

    
            print(f"Texting {phone_number}  \n\n Form : {form_link} \n\n  Msg: {sms} ")
            
            webbrowser.open(form_link)

            
            import pdb; pdb.set_trace();
            Txt_GoogleForm(sms,phone_number)
            
        except Exception as e:
            # Handle exceptions here
            import pdb; pdb.set_trace();
            print(f"An error occurred: {e}")
            continue
        
