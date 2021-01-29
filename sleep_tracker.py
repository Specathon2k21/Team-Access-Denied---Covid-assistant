import os
import datetime
import pyttsx3




def speak_s(text):

    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)

    engine.say(text)
    engine.runAndWait()

def sleeptime():
     
    if os.path.exists("goodnight.txt"):
        
        f = open("goodnight.txt", "r+")
        starttime = f.readlines()
        print(starttime)
        endtime = strTime = datetime.datetime.now().strftime("%H:%M:%S") 
        FMT = '%H:%M:%S'
        tdelta = datetime.datetime.strptime("07:30:00", FMT) - datetime.datetime.strptime("21:00:00", FMT)
        print(tdelta)
        indx = str(tdelta).index(',')
        t = str(tdelta)[indx+1:].replace(" ",'')
        speak_s("You have slept for "+t)
