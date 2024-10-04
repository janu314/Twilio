# Twilio
python flash.py
#Available Endpoints:
sms_reply: /sms-webhook
home: /
static: /static/<path:filename>
127.0.0.1 - - [19/Sep/2024 20:27:56] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [19/Sep/2024 20:27:56] "GET /favicon.ico HTTP/1.1" 404 -
127.0.0.1 - - [19/Sep/2024 20:30:08] "POST /sms-webhook HTTP/1.1" 200 -

#To acces the server
curl -X POST http://127.0.0.1:5000/sms-webhook \
     -d "Body=Hello, this is a test message" \
     -d "From=+1234567890"

