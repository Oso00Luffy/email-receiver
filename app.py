
import os
import imaplib
import email
from email.header import decode_header
from flask import Flask, render_template

app = Flask(__name__)

# Function to fetch verification codes
def fetch_verification_codes(email_user, email_pass, imap_server="imap.gmail.com"):
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_user, email_pass)
    
    # Select the inbox
    mail.select("inbox")

    # Search for all unread messages
    status, messages = mail.search(None, 'UNSEEN')

    # Convert messages to a list
    messages = messages[0].split(b' ')
    
    codes = []
    
    for msg_num in messages:
        # Fetch the email by ID
        _, msg_data = mail.fetch(msg_num, '(RFC822)')
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                # Parse the email content
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                
                # Check if the subject contains verification code
                if "verification code" in subject.lower():
                    # Extract the code from the email body
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                codes.append(body.strip())
                    else:
                        body = msg.get_payload(decode=True).decode()
                        codes.append(body.strip())

    return codes

@app.route('/')
def index():
    # Replace with your email credentials or set them as environment variables
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')

    codes = fetch_verification_codes(email_user, email_pass)

    return render_template('index.html', codes=codes)

if __name__ == "__main__":
    app.run(debug=True)
