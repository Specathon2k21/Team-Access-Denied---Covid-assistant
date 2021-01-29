import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import sys
import requests
import random
import tflearn
from tensorflow.python.framework import ops
import numpy
import json
import pickle
import pyttsx3
import speech_recognition as sr
from corona_tracker import corona_tracker
from corona_predictor import track_covid

import re
import spacy
import os
import os.path
import playsound
import time
import winsound
from datetime import datetime,timedelta
import multiprocessing
import sounddevice
from scipy.io import wavfile  


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtGui import QMovie
from PyQt5.uic  import loadUiType
from ass import Ui_Assistant



global data
with open("intents.json") as file:
    data = json.load(file)

try:
    
    with open("data.pickle",'rb') as f:
        words,labels,training,output = pickle.load(f)


except:

    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for pattern in intent["text"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["intent"])

        if intent["intent"] not in labels:
            labels.append(intent["intent"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)


    training = numpy.array(training)
    output = numpy.array(output)

    with open("data.pickle",'wb') as f:
        pickle.dump((words,labels,training,output),f)

ops.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

try:
    
    model.load("model.tflearn")

except:
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save("model.tflearn")


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
            
    return numpy.array(bag)



class Inputs(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Assistant()
        self.ui.setupUi(self)
    
    def speak_s(self,text):

        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)

        engine.say(text)
        engine.runAndWait()
    
    def take_input(self):
        
        obj = Main()
        
        r = sr.Recognizer()

        with sr.Microphone() as source:
            while True:
                try:
                   
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source)
                    string = r.recognize_google(audio)
                    return string
                except:
                    self.speak_s("I dont understand that")
                    continue

 
class AlarmThread(QThread):

    def __init__(self):
        super(AlarmThread,self).__init__()
        
    def ta_input(self):
        
        r = sr.Recognizer()

        with sr.Microphone() as source:
            
            try:
                print("Alarm input")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
                string = r.recognize_google(audio)
                return string
            except:
                return "no"

    
    def run(self):
        
        self.check()
    
    def check(self):
        obj = Inputs()
        while True:
            if os.path.exists("alarms.txt"):
                
                fs,data = wavfile.read('alarm.wav')
                with open("alarms.txt",'r') as f:
                    alarms =f.readlines()

                    for i in range(len(alarms)):
                        alarms[i] = alarms[i].replace("\n","")
                    for i in alarms:
                        curr_obj = datetime.now()
                        curr_time = '{:%H:%M %p}'.format(curr_obj)
                        curr_day = '{:%d-%m-%Y}'.format(curr_obj)
                        
                        curr_pattern = '{} {}'.format(curr_day,curr_time)
                        
                        if curr_pattern==i:
                            tm = i.split(":")[1].replace("AM","").replace("PM","")
                            curr_min = curr_obj.minute
                            while curr_min <= int(tm):
                                curr_min = datetime.now().minute
                                sounddevice.play(data,fs)
                                ala_inp = self.ta_input().lower()
                                if ala_inp == 'stop' or ala_inp=="shut up" or ala_inp=="ok" :
                                    obj.speak_s("ok mahesh")
                                    sounddevice.stop()
                                    break
                                

                        time.sleep(10)

    def stop(self):
        
        playsound.playsound('alarm.mp3',False)



class MedThread(QThread):

    def __init__(self):
        super(MedThread,self).__init__()
    
    def run(self):
        self.check()

    def ta_input(self):
        
        r = sr.Recognizer()

        with sr.Microphone() as source:
            
            try:
                print("med input")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
                string = r.recognize_google(audio)
                return string
            except:
                return "no"

    def check(self):
        obj = Inputs()
        with open("medication.txt","r") as med:
            meds = med.readlines()
        
        if len(meds)>0:
            for i in range(len(meds)):
                meds[i] = meds[i].replace("\n",'')
        
        if len(meds)>0:
          
            while True:
                curr_obj = datetime.now()
                curr_time = '{:%I:%M %p}'.format(curr_obj)
                for i in meds:
                    
                    if str(i) in curr_time:
                        fs,data = wavfile.read('medit.wav')
                        tm = str(i).split(':')[1].replace('AM','').replace('PM','')
                        for i in range(5):
                            curr_min = datetime.now().minute
                            sounddevice.play(data,fs)
                            ala_inp = self.ta_input().lower()
                            if ala_inp == 'stop' or ala_inp=="shut up" or ala_inp=="ok" :
                                obj.speak_s("ok mahesh")
                                sounddevice.stop()
                                break
                    print(curr_time)

                    time.sleep(10)
            

        

class MainThread(QThread):

    def __init__(self):
        super(MainThread,self).__init__()
    
    def run(self):
        
        self.chat()

    def speak_s(self,text):

        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)

        engine.say(text)
        engine.runAndWait()

    def take_input(self):
        
        r = sr.Recognizer()

        with sr.Microphone() as source:
            while True:
                try:
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source)
                    string = r.recognize_google(audio)
                    return string
                except:
                    
                    continue  
    
    def chat(self):
        
        with open("intents.json") as file:
            data = json.load(file)
        
        obj = Inputs()
        obj1 = AlarmThread()
        wake = "activate"
        
        while True:

            
            print("speak")
            active = self.take_input().lower()
            
            #active = "activate"
            print(active)
                
            if active.count(wake) > 0:
                if os.path.exists("initial.txt"):
                    playsound.playsound('chime.mp3')
                    self.speak_s("How may i help you?")
                else:
                    with open("initial.txt",'w') as f:
                        
                        playsound.playsound('power up.mp3')
                        self.speak_s("Hello mahesh,i am always here to help you")
                

                print("\n\n\t\t\t Started")

                #self.speak_s("Start talking with the bot (type quit to stop)!")

                inp = obj.take_input() 
                #inp = "vitamin c tablet at 9 am"
                print(inp)

                if inp.lower() == "quit":
                    break

                if 'alarm'  in inp.lower() or 'wake' in inp.lower():

                    
                    next_days = ['today','tomorrow']

                    nlp = spacy.load('en_core_web_sm')
                    doc = nlp(inp)
                    entities = []
                    for ent in doc.ents:
                        entities.append(ent)
                    print(entities)
                    
                    if len(entities)==1:

                        
                        inp_split = str(entities[0]).split()

                        if inp_split[1].lower()=="hours":

                            day_after_adding = datetime.now() + timedelta(hours=int(inp_split[0]))
                            formatted_time = '{:%H:%M %p}'.format(day_after_adding)
                            formatted_day = '{:%d-%m-%Y}'.format(day_after_adding)

                            data = '{} {}\n'.format(formatted_day,formatted_time)
                        
                        elif inp_split[1].lower()=="minutes":
                            
                            print(inp_split)
                            day_after_adding = datetime.now() + timedelta(minutes=int(inp_split[0]))
                            formatted_time = '{:%H:%M %p}'.format(day_after_adding)
                            formatted_day = '{:%d-%m-%Y}'.format(day_after_adding)

                            data = '{} {}\n'.format(formatted_day,formatted_time)
                        
                        elif inp_split[1].lower()=="seconds":
                            
                            print(inp_split)
                            day_after_adding = datetime.now() + timedelta(seconds=int(inp_split[0]))
                            formatted_time = '{:%H:%M %p}'.format(day_after_adding)
                            formatted_day = '{:%d-%m-%Y}'.format(day_after_adding)

                            data = '{} {}\n'.format(formatted_day,formatted_time)

                        
                        with open("alarms.txt",'a') as f:
                            f.write(data)
                        


                
                elif "future" in inp.lower() or 'prediction' in inp.lower():
                    self.speak_s("How many days :")
                    days = self.take_input()
                    print(days)

                    days = re.findall(r'\d+', days)
                    value = track_covid(int(days[0]))
                    self.speak_s("There is a high chance of covid cases to increase ,to be accurate the cases would be "+"{:,} by {} days".format(value,days))

                elif 'covid' in inp.lower() or 'covid-19' in inp.lower() or 'corona' in inp.lower() or 'covid 19' in inp.lower():
                    d = corona_tracker(inp)
                    self.speak_s("Total confirmed cases are "+"{:,}".format(d['confirmed']))
                    self.speak_s("Total deaths are "+"{:,}".format(d['deaths']))
                    self.speak_s("Total recovered cases are "+"{:,}".format(d['recovered']))
                
                elif 'play music' in inp.lower() :
                    fs,data = wavfile.read('go.wav')                    
                    sounddevice.play(data,fs)
                    while True:
                        ala_inp = self.take_input().lower()
                        print(ala_inp)
                        if ala_inp == 'top' or ala_inp == 'stop' or ala_inp=="shut up" or ala_inp=="ok" :
                            obj.speak_s("ok mahesh")
                            sounddevice.stop()
                            break

                
                elif 'medication' in inp.lower() or "schedule" in inp.lower() or 'medicine' in inp.lower():
                    
                    nlp = spacy.load('en_core_web_sm')
                    doc = nlp(inp.lower())
                    entities = []
                    for ent in doc.ents:
                        entities.append(ent)
                    
                    
                    s_time = str(entities[0]).replace(".","")
                    ap = ''
                    indx = -1
                    for i in range(len(s_time)):
                        if s_time[i].isalpha():
                            indx = i
                            break
                    
                    time = s_time[:indx]+s_time[indx:].upper()

                   
                    
                    with open("medication.txt",'a') as med:
                        med.write(time+"\n")
                    
                    self.speak_s("Medication time has been recorded")

                elif 'temperature' in inp.lower() or 'weather' in inp.lower() or "weather report" :
                    self.speak_s("which city's weather would you like to know?")
                    city = self.take_input()

                    api = "http://api.openweathermap.org/data/2.5/weather?q={}&appid=bd403e5f29e5d5809fe3b267b948ed09".format(city)
                    api_res = requests.get(api)
                    json_obj = json.loads(api_res.text)
                    tempk = int(json_obj['main']['temp'])
                    tempC = tempk-273.15
                    self.speak_s("Weather in {} right now is {} degree celsius".format(city,tempc))

                else:
                    results = model.predict([bag_of_words(inp, words)])
                    results_index = numpy.argmax(results)
                    tag = labels[results_index]
                    
                    for tg in data["intents"]:
                        if tg['intent'] == tag:
                            responses = tg['responses']
                    if responses in ["See you later","Have a nice day","Bye! `Come` back again soon."]:
                        os.remove('initial.txt')
                    self.speak_s(random.choice(responses))
                
            


startExecution = MainThread()
alarm = AlarmThread()
med = MedThread()


class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Assistant()
        self.ui.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.ui.pushButton.clicked.connect(self.close)
        self.startTask()
    
    def startTask(self):
        self.ui.movie = QtGui.QMovie("aaass.gif")
        self.ui.label.setMovie(self.ui.movie)
        self.ui.movie.start()
        self.ui.label_2.setText("Listening...")
       
        startExecution.start()
        alarm.start()
        med.start()


    def change_text(self):
        self.ui.label_2.setStyleSheet("background-color: yellow;  border: 1px solid black;") 

    

   


app = QApplication(sys.argv)
assistant = Main()
assistant.show()
exit(app.exec_())

