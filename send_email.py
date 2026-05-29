import smtplib
import os
import ssl
from dotenv import load_dotenv
from email.message import EmailMessage

#load creditentials from .env file
load_dotenv() #we load the content from the .env file
sender_email = os.getenv("EMAIL_ADRESS") # we get the email adress
email_password = os.getenv("EMAIL_PASSWORD") #we get the password

server = None #Initializing the server as None so the finally block won't crash because it the connection fails it jumps straight to the finally even with errors

#STMP Server configuration
host = "smtp.gmail.com" #the host, it's very important because it allows us to create a connection between smtp and gmail
port = 587 #STARTTLS #its the default recommended stmp port for modern email submission

#Create a secure SSL context
context = ssl.create_default_context() #allowing us to protect the message from bad persons, creating a safe before sending it

msg = EmailMessage() #we set up the msg, first we set up and email message object
msg["Subject"] = "Check the email i sent you!!" #we set the subject
msg["From"] = sender_email #we set the sender
msg["To"] = "foucault.audran@gmail.com" #we set the recipient
msg.set_content("This is a test email") #and we set the msg content
 
#better way to write the try block:
try:
    with smtplib.SMTP(host, port) as server:
        server.ehlo() #Say hello (initial command used in an SMTP session to introduce the sending server to the receiving one)
        server.starttls(context = context) #we put on the armored package around the message
        server.login(sender_email, email_password) #we identify
        server.send_message(msg)
    print("SENT")
except Exception as e:
    print("ERROR:", e)
#no finally needed since with open closes automatically