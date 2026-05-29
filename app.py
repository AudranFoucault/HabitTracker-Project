from flask import Flask, render_template, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime, date, timedelta



#What V1 must do (today) Show page (done) / Add habit (name + frequency per week)(done) Save to data/habits.json (done) Read habits and display on page load (done)
load_dotenv()
app = Flask(__name__)
CORS(app)
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add", methods=["POST"])
def add():
    #STEP 1: on log ce qui arrive
    payload = request.get_json(force=True)
    print("PAYLOAD:", payload)
    #STEP 2: ON creer un dictionnaire(avec securite pour les valeurs)
    #on recupere les valeurs du payload ou des valeurs par defauts si y'en a pas
    item = {
        "habit": payload.get("habit", "not defined"),
        "per_week": int(payload.get("per_week", 7)),
        "left": int(payload.get("left", 7)), #left = per_week au debut
        "streak" : "",
        "completion": []
    }
    #STEP 3: Meme file pattern qu'avant
    #1. Read
    try:
         
        with open("habits.json", "r") as file:
            data = json.load(file)
    except:
        data = []
        #2. Append
    data.append(item)
        #3. Dump and return
    with open("habits.json", "w") as file:
        json.dump(data, file, indent=4)
    return json.dumps(data)


@app.route("/read_habits", methods=["GET"])
def read():
    with open("habits.json", 'r') as file:
        data = json.load(file)
    return json.dumps(data)

@app.route("/delete", methods=["POST"])
def delete():
    with open("habits.json", "r") as file:
        data = json.load(file)
        habit_index = request.get_json(force=True)["index"]
        data.pop(int(habit_index))
          
    with open("habits.json", "w") as file:
        json.dump(data, file)
    return json.dumps(data)

@app.route("/done", methods=["POST"])
def done():
    with open("habits.json", "r") as file:
        data = json.load(file)
        habit_completion = str(date.today())
        index = request.get_json(force=True)["index"]
        data[index]["left"] -= 1
        data[index]["completion"].append(habit_completion)
        completions = data[index]["completion"]
        print("compdate", completions)
    with open("habits.json", "w") as file:
        json.dump(data, file, indent=4)
    return json.dumps(data)

@app.route("/increment", methods=["POST"])
def increment():
    with open("habits.json", "r") as file:
        data = json.load(file)
        index = request.get_json(force=True)["index"]
        data[index]["left"] += 1
    with open("habits.json", "w") as file:
        json.dump(data, file, indent=4)
    return json.dumps(data)

@app.route("/streak", methods=["POST"])
def streak():
    with open("habits.json", "r") as file:
        data = json.load(file)
        index = request.get_json(force=True)["index"]
        completions = data[index]["completion"]
        date_format = '%Y-%m-%d'
        date_objects = [datetime.strptime(completion, date_format).date() for completion in completions]

        if len(date_objects) >= 2 and date_objects[-1] - date_objects[-2] == timedelta(days=1):
            try:
                data[index].update({"streak": "WELL DONE, KEEP THE GOOD WORK!"})
                print("modified")
            except IndexError:
                print("IndexError:", IndexError)
        else:
            data[index].update({"streak": "Have you been doing this habit for 2 days or more, if not that's why"})
            print("modified but sum's missing")
        
    with open("habits.json", "w") as file:
        json.dump(data, file, indent=4)
    return json.dumps(data)

def email_function():
    with app.app_context():

        print("function is running")
        load_dotenv()
        with open("habits.json", "r") as file:
            print("file opened")
            data = json.load(file)
            for habit in data:
                
                summary_string = str(habit["habit"]) + "\n" + str(habit["left"]) + "\n" + str(habit["completion"])
                print(summary_string)
        with open("habits.json", "w") as file:
            json.dump(data, file)
        sender_email = os.getenv("EMAIL_ADRESS") # we get the email adress
        email_password = os.getenv("EMAIL_PASSWORD") #we get the password

        server = None #Initializing the server as None so the finally block won't crash because it the connection fails it jumps straight to the finally even with errors

        #STMP Server configuration
        host = "smtp.gmail.com" #the host, it's very important because it allows us to create a connection between smtp and gmail
        port = 587 #STARTTLS #its the default recommended stmp port for modern email submission

        #Create a secure SSL context
        context = ssl.create_default_context() #allowing us to protect the message from bad persons, creating a safe before sending it

        msg = EmailMessage() #we set up the msg, first we set up and email message object
        msg["Subject"] = "Hello, here's your detailed daily check-up. Have a blessed day" #we set the subject
        msg["From"] = sender_email #we set the sender
        msg["To"] = "foucault.audran@gmail.com" #we set the recipient
        msg.set_content(summary_string) #and we set the msg content
 
#better way to write the try block:
        try:
            with smtplib.SMTP(host, port) as server:
                print("message preparing")
                server.ehlo() #Say hello (initial command used in an SMTP session to introduce the sending server to the receiving one)
                server.starttls(context = context) #we put on the armored package around the message
                server.login(sender_email, email_password) #we identify
                server.send_message(msg)
                print("message sent")
            print("SENT")
        except Exception as e:
            print("ERROR:", e)
email_function()
#no finally needed since with open closes automatically



    
     
       
     