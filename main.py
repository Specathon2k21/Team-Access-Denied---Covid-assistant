import pyttsx3
import playsound
import datetime
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
import datetime
import time 
import speech_recognition as sr
from corona_tracker import corona_tracker
import re



engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def take_input():

    r = sr.Recognizer()

    with sr.Microphone() as source:

        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    
    string = r.recognize_google(audio)
    return string



def speak(text):
    engine.say(text)
    engine.runAndWait()


#initialization
def start():
    

    speak("Starting Engine")
    speak("Collecting required resources")
    speak("initializing")
    speak("Getting information from the CPU")
    speak("contacting with mail services")
    playsound.playsound('power up.mp3')

    """name="Mahesh"
    age="21"
    email_id="mahesh6273766@gmail.com"
    email_id_password="M@hesh6273766reddy"
    gender="Sir"
    city="Hyderabad"
    dad="maheshdrago@gmail.com"
    mom="maheshmahesh6273766@gmail.com"

    account_sid = 'AC434176463ac6157e4f781e2ead50ef4a'
    auth_token = '4ae968293c73a34c350c6438957536a1'

    client = Client(account_sid,auth_token)"""


def main():

    speak("Hhi mahesh!")

    while True:

        text = take_input()
        print(text)
        if "stop"==text.lower():
            speak("Bye signing off")
            break
        else:
            d = corona_tracker(text)
            speak("Total confirmed cases are "+"{:,}".format(d['confirmed']))
            speak("Total deaths are "+"{:,}".format(d['deaths']))
            speak("Total recovered cases are "+"{:,}".format(d['recovered']))
            
            speak("Do you want more help?")
            inp = take_input()
            if inp.lower()=="yes":
                print(inp)
                continue
            else:
                speak("bye signing off")
                break

main()











