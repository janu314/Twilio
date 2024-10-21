from flask import Flask, request, jsonify, url_for
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPBASE_URL = os.getenv('SUPBASE_URL')
SUPBASE_KEY = os.getenv('SUPBASE_KEY')
supabase = create_client(SUPBASE_URL, SUPBASE_KEY)

app = Flask(__name__)

# Helper function to store messages in Supabase
def store_message(sender, recipient, message_content):
    created_at = datetime.now().isoformat()
    print(f"Storing message: {message_content} from {sender} to {recipient} at {created_at}")

    response = supabase.table('SMS').insert({
        "created_at": created_at,
        "from": sender,
        "to": recipient,
        "message": message_content
    }).execute()

    if response.data:
        print("Message stored successfully.")
    else:
        print(f"Failed to store message. Error: {response.error}")


@app.route('/sms-webhook', methods=['POST'])
def sms_reply():
    # Get the incoming message from the user
    incoming_message = request.form['Body']
    from_number = request.form['From']  # User's phone number
    to_number = request.form['To']      # Your Twilio number

    # Log the incoming message
    print(f"Incoming message: {incoming_message} from {from_number} to {to_number}")

    #Prepare the response message
    outgoing_message = (
        f"Hello, you said: {incoming_message}\n\n"
        "Please note: This is an automated message: "
        "For questions, email support at clinic.notes3@gmail.com.\n\n"
        "If you requested a language change, it will be implemented in our next version 2.0."
    )

    # Store the incoming message
    store_message(from_number, to_number, incoming_message)

    # Store the outgoing message
    store_message(to_number, from_number, outgoing_message)

    # Create Twilio response
    resp = MessagingResponse()
    resp.message(outgoing_message)

    return str(resp)


# Root endpoint
@app.route("/", methods=['GET'])
def home():
    endpoints = {
        "sms_webhook": url_for('sms_reply', _external=True)
    }
    return f"Available endpoints: {endpoints}"

# Print all available endpoints on startup
@app.before_first_request
def print_endpoints():
    print("Available Endpoints:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))  # Default to 5001 if PORT is not set
    app.run(host="0.0.0.0", port=port, debug=True)

